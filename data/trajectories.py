import logging
import math

import numpy as np

import torch
from torch.utils.data import Dataset

logger = logging.getLogger(__name__)

def read_file(_path, delim='  '):
    data = []
    with open(_path, 'r') as f:
        for line in f:
            line = line.strip().split(delim)
            line = [float(i) for i in line]
            data.append([line[0],line[1],line[2],line[4]])
    return np.asarray(data)


class TrajectoryDataset(Dataset):
    def __init__(
        self, data_dir, obs_len=8, pred_len=12, min_ped=1, delim='  '
    ):
        """
        Args:
        - data_dir: path of obsmat.txt
        <frame_id> <ped_id> <x> <y>
        - obs_len: Number of time-steps in input trajectories
        - pred_len: Number of time-steps in output trajectories
        - min_ped: Minimum number of pedestrians that should be in a seqeunce
        - delim: Delimiter in the dataset files
        """
        super(TrajectoryDataset, self).__init__()

        self.data_dir = data_dir
        self.obs_len = obs_len
        self.pred_len = pred_len
        self.seq_len = self.obs_len + self.pred_len
        self.delim = delim

        num_peds_in_seq = []
        seq_list = []
        seq_list_rel = []
        frame_seq = []

        data = read_file(self.data_dir, delim)
        frames = np.unique(data[:, 0]).tolist()
        frame_data = []
        for frame in frames:
            frame_data.append(data[frame == data[:, 0], :])
        num_sequences = int(
            math.ceil(len(frames) - self.seq_len + 1))

        for idx in range(0, num_sequences + 1):
            curr_seq_data = np.concatenate(
                frame_data[idx:idx + self.seq_len], axis=0)
            peds_in_curr_seq = np.unique(curr_seq_data[:, 1])

            curr_seq = np.zeros((len(peds_in_curr_seq), 2, self.seq_len))

            num_peds_considered = 0

            for _, ped_id in enumerate(peds_in_curr_seq):
                curr_ped_seq = curr_seq_data[curr_seq_data[:, 1] ==
                                             ped_id, :]
                curr_ped_seq = np.around(curr_ped_seq, decimals=4)
                pad_front = frames.index(curr_ped_seq[0, 0]) - idx
                pad_end = frames.index(curr_ped_seq[-1, 0]) - idx + 1
                if pad_end - pad_front != self.seq_len:
                    continue
                curr_ped_seq = np.transpose(curr_ped_seq[:, 2:])

                _idx = num_peds_considered
                curr_seq[_idx, :, pad_front:pad_end] = curr_ped_seq

                num_peds_considered += 1

            if num_peds_considered > min_ped:

                num_peds_in_seq.append(num_peds_considered)
                seq_list.append(curr_seq[:num_peds_considered])
                frame_seq.append(frames[idx])

        self.num_seq = len(seq_list)
        seq_list = np.concatenate(seq_list, axis=0)

        # Convert numpy -> Torch Tensor
        self.obs_traj = torch.from_numpy(
            seq_list[:, :, :self.obs_len]).type(torch.float)
        self.pred_traj = torch.from_numpy(
            seq_list[:, :, self.obs_len:]).type(torch.float)
        self.frame_seq = frame_seq
        cum_start_idx = [0] + np.cumsum(num_peds_in_seq).tolist()
        self.seq_start_end = [
            (start, end)
            for start, end in zip(cum_start_idx, cum_start_idx[1:])
        ]

    def __len__(self):
        return self.num_seq

    def __getitem__(self, index):
        start, end = self.seq_start_end[index]
        out = [
            self.obs_traj[start:end, :], self.pred_traj[start:end, :],
            self.frame_seq[index]
        ]
        return out

# if __name__ == '__main__':
#     data_dir = '../seq_hotel/obsmat.txt'
#     dset = TrajectoryDataset(data_dir)
#     print(dset[0][2])
