import argparse

import torch
import torch.nn as nn
import torch.optim as optim

from mnist_classification.data_loader import get_loaders
from mnist_classification.trainer import Trainer

from mnist_classification.models.fc_model import FullyConnectedClassifier
from mnist_classification.models.cnn_model import ConvolutionalClassifier
from mnist_classification.models.rnn_model import SequenceClassifier

def define_argparser():
    p = argparse.ArgumentParser()

    p.add_argument('--model_fn', required=True)
    p.add_argument('--gpu_id', type=int, default=0 if torch.backends.mps.is_available() else -1) # torch.cuda.is_available()

    p.add_argument('--train_ratio', type=float, default=.8)

    p.add_argument('--batch_size', type=int, default=256)
    p.add_argument('--n_epochs', type=int, default=20)
    p.add_argument('--verbose', type=int, default=2)

    p.add_argument('--model', type=str, default='fc')

    p.add_argument('--hidden_size', type=int, default=64)
    p.add_argument('--n_layers', type=int, default=4)
    p.add_argument('--dropout_p', type=float, default=.2)

    p.add_argument('--max_grad', type=float, default=-1)

    config = p.parse_args()

    return config


def get_model(config):
    if config.model == 'fc':
        model = FullyConnectedClassifier(28**2, 10)
    elif config.model == 'cnn':
        model = ConvolutionalClassifier(10)
    elif config.model == 'rnn':
        model = SequenceClassifier(
            input_size = 28,
            hidden_size = config.hidden_size,
            output_size = 10,
            n_layers = config.n_layers,
            dropout_p = config.dropout_p,
        )
    else:
        raise NotImplementedError('You need to specify model name.')

    return model


def main(config):
    # Set device based on user defined configuration.
    device = torch.device('cpu') if config.gpu_id < 0 else torch.device('mps:%d' % config.gpu_id)

    train_loader, valid_loader, test_loader = get_loaders(config)

    print("Train:", len(train_loader.dataset))
    print("Valid:", len(valid_loader.dataset))
    print("Test:", len(test_loader.dataset))

    model = get_model(config).to(device)
    optimizer = optim.Adam(model.parameters())
    crit = nn.NLLLoss()

    if config.verbose >= 2:
        print(model)
        print(optimizer)
        print(crit)

    trainer = Trainer(config)
    trainer.train(model, crit, optimizer, train_loader, valid_loader)

if __name__ == '__main__':
    config = define_argparser()
    main(config)
