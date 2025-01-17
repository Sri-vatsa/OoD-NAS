import os
import sys
import argparse
import os.path as osp
import torch.backends.cudnn as cudnn
cudnn.benchmark = True
cudnn.enabled = True
import numpy as np
import torch

sys.path.insert(0, osp.join(osp.dirname(osp.abspath(__file__)), '../'))

from nas_ood_single import Trainer
from torch.utils.data import DataLoader

from tensorboardX import SummaryWriter

import datetime
import logging


def get_args():
    parser = argparse.ArgumentParser("ood-nas-single")
    parser.add_argument('--data', type=str, default='~/data', help='location of the data corpus')
    parser.add_argument('--dataset', type=str, default='nico_animal', choices=['nico_animal', 'nico_vehicle', 'pacs'])
    parser.add_argument('--batch_size', type=int, default=16, help='batch size')
    parser.add_argument('--proj_dims', type=int, default=7, help='proj dimensions')
    parser.add_argument('--sparseness', type=int, default=2, help='sparseness')
    parser.add_argument('--num_classes', type=int, default=10, help='num_classes')
    parser.add_argument('--learning_rate', type=float, default=0.025, help='init learning rate')
    parser.add_argument('--learning_rate_min', type=float, default=0.001, help='min learning rate')
    parser.add_argument('--momentum', type=float, default=0.9, help='momentum')
    parser.add_argument('--weight_decay', type=float, default=3e-4, help='weight decay')
    parser.add_argument('--report_freq', type=float, default=50, help='report frequency')
    parser.add_argument('--init_channels', type=int, default=36, help='num of init channels')
    parser.add_argument('--gpu', type=int, default=0, help='gpu device id')
    parser.add_argument('--epochs', type=int, default=20, help='num of training epochs')
    parser.add_argument('--layers', type=int, default=20, help='total number of layers')
    parser.add_argument('--steps', type=int, default=4, help='total number of layers')
    parser.add_argument('--model_path', type=str, default='saved_models', help='path to save the model')
    parser.add_argument('--cutout', action='store_true', default=False, help='use cutout')
    parser.add_argument('--cutout_length', type=int, default=16, help='cutout length')
    parser.add_argument('--drop_path_prob', type=float, default=0.2, help='drop path probability')
    parser.add_argument('--save', type=str, default='EXP', help='experiment name')
    parser.add_argument('--seed', type=int, default=5, help='random seed')
    parser.add_argument('--grad_clip', type=float, default=5, help='gradient clipping')
    parser.add_argument('--train_portion', type=float, default=0.5, help='portion of training data')
    parser.add_argument('--auxiliary', action='store_true', default=False, help='use one-step unrolled validation loss')
    parser.add_argument('--auxiliary_weight', type=float, default=0.4, help='init learning rate')
    parser.add_argument('--arch_learning_rate', type=float, default=3e-4, help='learning rate for arch encoding')
    parser.add_argument('--arch_weight_decay', type=float, default=1e-3, help='weight decay for arch encoding')
    parser.add_argument('--targetdomain', type=str, default="cartoon", help='domain in pacs to be removed unless in testing')
    parser.add_argument('--root_saves_concept_path', type=str, default='/storage/home/hcocice1/sp308/NAS-OoD/saves_concept/')
    parser.add_argument('--root_saves_category_path', type=str, default='/storage/home/hcocice1/sp308/NAS-OoD/saves_category/')
    parser.add_argument('--val_type', type=str, default=None) # Seems like a dummy value; keeping it for compatibility with functions
    parser.add_argument('--lambda_cycle', type=float, default=10, help='balance for cycle loss')
    parser.add_argument('--start_epoch', type=int, default=0, help='start epoch to add synthetic to train set')
    parser.add_argument('--ratio', type=float, default=0.5, help='ratio to add synthetic data to train set')
    parser.add_argument('--lambda_lr', type=float, default=0.0001, help='balance for generator learning rate')
    parser.add_argument('--lambda_ot', type=float, default=0.01, help='balance for optimal transport distance loss')
    parser.add_argument('--lambda_ce', type=float, default=0.01, help='balance for generator cross entropy loss')
    parser.add_argument('--backbone_class', type=str, default='ConvNet', help='backbone for domain classifier')
    parser.add_argument('--stage1_ratio', type=float, default=1, help='ratio to add synthetic data to train set')

    parser.add_argument('--root_path', type=str, default='/storage/home/hcocice1/sp308/data/PACS/')

    #args = parser.parse_args()
    args, unknown_args = parser.parse_known_args()
    
    save_path1 = '{}-{}-{}-num_classes-{}'.format(args.dataset, args.proj_dims, args.sparseness, args.num_classes)
    save_path2 = '_'.join([str(args.learning_rate), str(args.arch_learning_rate), str(args.batch_size), 
                           str(args.epochs), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    args.save_dir = '/storage/home/hcocice1/sp308/train_out/'

    args.save_path = os.path.join(args.save_dir, save_path1, save_path2)
    args.save_path1 = os.path.join(args.save_dir, save_path1)


    create_exp_dir(args.save_path1)
    create_exp_dir(args.save_path)    

    return args

def create_exp_dir(path):
    if not os.path.exists(path):
        # os.mkdir(path)
        os.makedirs(path, exist_ok=True)
    print('Experiment dir : {}'.format(path))


def get_loader(args):

    if args.dataset == 'nico_animal':
        from dataloader.nico_animal import NicoAnimal as Dataset
        args.dropblock_size = 5
        trainset = Dataset('animal_train_ood', args, augment=True)
        valset = Dataset('animal_val_ood', args)
        testset = Dataset('animal_test_ood', args)

    elif args.dataset == 'nico_vehicle':
        from dataloader.nico_vehicle import NicoVehicle as Dataset
        args.dropblock_size = 5
        trainset = Dataset('vehicle_train_ood', args, augment=True)
        valset = Dataset('vehicle_val_ood', args)
        testset = Dataset('vehicle_test_ood', args)

    elif args.dataset == 'pacs':
        from dataloader.pacsLoader import pacsDataset as Dataset
        trainset = Dataset('train', args)
        valset = Dataset('val', args)
        testset = Dataset('test', args)
        
    elif args.dataset == 'finger':
        from model.dataloader.fingerprintLoader import FingerDataset as Dataset
        trainset = Dataset('train', args)
        valset = Dataset('val', args)
        testset = Dataset('test', args)
    else:
        raise ValueError('Non-supported Dataset.')

    args.num_class = trainset.num_class
    args.num_classes = trainset.num_class
    args.num_concept = trainset.num_concept

    train_loader = DataLoader(dataset=trainset, batch_size=args.batch_size, shuffle=True, pin_memory=True, num_workers=2)
    val_loader = DataLoader(dataset=valset, batch_size=args.batch_size, shuffle=False, pin_memory=True, num_workers=2)
    test_loader = DataLoader(dataset=testset, batch_size=args.batch_size, shuffle=False, pin_memory=True, num_workers=2)

    return train_loader, val_loader, test_loader


def main():
    args = get_args()
    
    log_format = '%(asctime)s %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
        format=log_format, datefmt='%m/%d %I:%M:%S %p')
    fh = logging.FileHandler(os.path.join(args.save_path, 'log.txt'))
    fh.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(fh)    
    
    logging.info(vars(args))
    
    if torch.cuda.is_available():
        torch.backends.cudnn.enabled = True
        torch.backends.cudnn.benchmark = True
        
    
    torch.cuda.set_device(args.gpu)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)
    
    writer = SummaryWriter(args.save_path)

    train_loader, val_loader, test_loader = get_loader(args)

    trainer = Trainer(args, logging, writer)

    trainer.train(train_loader, val_loader, test_loader)

    writer.close()

if __name__ == "__main__":
    main()