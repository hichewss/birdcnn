# -*- coding: utf-8 -*-
"""MLab Colab Notebook - jenuity

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18RpS5V9qVhiWw7taxm_JohW1mpiSfqq3

# MLab Onboarding Project, Fall 2022

Your task is to classify different species of birds! See the project document pinned in \#mlab-general for more details.

## Setup
"""

# Commented out IPython magic to ensure Python compatibility.
# this mounts your Google Drive to the Colab VM.
from google.colab import drive
drive.mount('/content/drive')

# enter the foldername in your Drive where you have saved the unzipped
# workshop folder, e.g. 'acmlab/project'
FOLDERNAME = 'acmlab/project'
assert FOLDERNAME is not None, "[!] Enter the foldername."

# now that we've mounted your Drive, this ensures that
# the Python interpreter of the Colab VM can load
# python files from within it.
import sys
PATH = '/content/drive/Shared drives/{}'.format(FOLDERNAME)
sys.path.append(PATH)

# %cd $PATH

# Math/deep learning libraries
import numpy as np
import torch
from torch import nn

# Data processing
import pandas as pd

# Data transformations
import torchvision

# Loading images/bundles of images
from PIL import Image
import h5py

# Plotting
import matplotlib.pyplot as plt

# Progress bars
import tqdm

# Other
import time
from datetime import date

from utils import load_data

# Set PyTorch to use the GPU
device = torch.device('cuda')

"""## Dataset

You'll need to create a way to load our training images into PyTorch.

Ordinarily, you would load images one at a time from a folder on your computer (or in our case, Google Drive). However, since Google Drive's file reading speed is extremely slow (on the order of 1 hour for the training dataset), this is inefficient for developing a model. Note that this *wouldn't* be the case if we were running locally, where file reading is much faster.

Since we still want you to get experience with creating an image dataset, we'll have you create it the traditional way (by loading images one at a time) on a **small dataset** that won't be used for actual training.

For the actual training dataset, we created an `h5py` bundle of the data, which allows you to read a single (larger) file to get a full list of images. Instead of reading the images individually, you'll be able to use the functions provided in `utils.py` to load lists of the images, labels, and classes.

### Loading images individually

Fill in the following class to load images one by one into a dataset. We provide a `csv_path` as an argument.

1. Load the CSV file using Pandas. The CSV is formatted as follows:
```
filepath,label,class
small_data/0 - GREAT XENOPS/0_1.jpg,0,GREAT XENOPS
...
small_data/2 - OSPREY/2_15.jpg,2,OSPREY
```

2. For each row of the CSV, read in the image at the `filepath`, and add the image and label to the `self.images` and `self.labels` list.

  We can load images with `Image.open(filename)`.

  We'll also want to keep track of the classes themselves, so `self.classes[0]` should equal the name of the bird with label 0 (`"GREAT XENOPS"`).

3. Fill in the rest of the functions based on the `self.images`, `self.labels`, and `self.classes` variables.
"""

class BirdDatasetSmall(torch.utils.data.Dataset):
    def __init__(self, csv_path):
        self.images = []
        self.labels = []
        self.classes = []

        df = pd.read_csv(csv_path)
        for index, row in df.iterrows():
          image = row["filepath"]
          self.images.append(Image.open(image))
          self.labels.append(row["label"])

          if row["class"] not in self.classes:
            self.classes.append(row["class"])
        
        assert len(self.images) == len(self.labels)
    
    def __len__(self):
        """Returns the number of examples in the dataset"""
        return len(self.images)
    
    def num_classes(self):
        """Returns the number of classes in the dataset"""
        return len(self.classes)
    
    def get_class(self, label):
        """Returns the name of the bird corresponding to the given label value"""
        return self.classes[label]

    def get_image(self, idx):
        """Returns the image of the idx'th example in the dataset"""
        return self.images[idx]

    def get_label(self, idx):
        """Returns the label of the idx'th example in the dataset"""
        return self.labels[idx]
    
    def __getitem__(self, idx):
        """Returns a tuple of the image and label of the idx'th example in the dataset"""
        return self.images[idx], self.labels[idx]
    
    def display(self, idx):
        """Displays the image at a given index"""
        display(self.get_image(idx))

"""#### Testing BirdDatasetSmall

First, we'll run some basic tests to make sure the dataset is reading the right values. The first time you run this cell, it might take about a minute to load the data.
"""

def test_case(message, value, expected_value):
    print(message)
    if value == expected_value:
        print("  PASSED")
    else:
        print(f"  EXPECTED: {expected_value}")
        print(f"  GOT: {value}")
    
small_dataset = BirdDatasetSmall("small_data.csv")

test_case("Length of the dataset", len(small_dataset), 45)
test_case("Label of idx=17", small_dataset.get_label(17), 1)

"""Next, we'll display some images from the dataset. The output of running the cell should match the following image:

![](https://drive.google.com/uc?export=view&id=1mqvn-KXh8mWV6HcxulAnNqDhIPPWCq6f)
"""

# Display some images from all_data
figure = plt.figure(figsize=(15, 10))
num_rows = 1
num_cols = 3

ds_idx = [13, 29, 43]
for plot_idx, idx in enumerate(ds_idx):
    ax = plt.subplot(num_rows, num_cols, plot_idx + 1) # subplot indices begin at 1, not 0
    ax.title.set_text(small_dataset.get_class(small_dataset.get_label(idx)))
    plt.axis('off')
    plt.imshow(small_dataset.get_image(idx))

"""### Loading images from a bundle

As mentioned previously, for Colab performance reasons we'll be loading all the training data from a pre-created HDF5 bundle.

You'll be filling in the same code as the previous dataset, but instead of loading images one by one, you will use the `utils.load_data()` function, which returns a tuple of a list of images, a list of labels, and a list of classes.

The other difference is the inclusion of a `transform` parameter. This is a `torchvision` Transform that should be applied to each image in `__getitem__` before returning.
"""

class BirdDataset(torch.utils.data.Dataset):
    def __init__(self, transform=None):
        self.images = []
        self.labels = []
        self.classes = []
        self.transform = transform

        ######## BEGIN YOUR CODE HERE ########
        loaded = load_data()
        self.images = loaded[0]
        self.labels = loaded[1]
        self.classes = loaded[2]
        ######### END YOUR CODE HERE #########
        
        assert len(self.images) == len(self.labels)
    
    def __len__(self):
        """Returns the number of examples in the dataset"""
        return len(self.images)
    
    def num_classes(self):
        """Returns the number of classes in the dataset"""
        return len(self.classes)
    
    def get_class(self, label):
        """Returns the name of the bird corresponding to the given label value"""
        return self.classes[label]

    def get_image(self, idx):
        """Returns the image of the idx'th example in the dataset"""
        return self.images[idx]

    def get_label(self, idx):
        """Returns the label of the idx'th example in the dataset"""
        return self.labels[idx]
    
    def __getitem__(self, idx):
        """Returns a tuple of the image and label of the idx'th example in the dataset"""
        return self.transform(self.images[idx]), self.labels[idx]

    def display(self, idx):
        """Displays the image at a given index"""
        display(self.get_image(idx))

"""## Creating and visualizing the dataset

First, let's create the `BirdDataset`. Be sure to pass in the transform as a parameter. We're using a `ToTensor()` transform to ensure that when PyTorch goes through the dataset, it reads the images as Tensors instead of images.

The first time you run this cell, it'll take about a minute to load the file.
"""

transform = torchvision.transforms.Compose([
    torchvision.transforms.ToTensor(),
])

all_data = BirdDataset(transform)

"""### Visualizing the data

An important part of deep learning is to understand what type of data we're working with. Here, we'll visualize some of the examples of our training set.
"""

# Display some images from all_data
figure = plt.figure(figsize=(15, 10))
num_rows = 8
num_cols = 8
for plot_idx in range(20):
    ax = plt.subplot(num_rows, num_cols, plot_idx + 1) # subplot indices begin at 1, not 0
    idx = (plot_idx * 373) % len(all_data) # Gets a "random" index in the dataset

    # for this code, use `idx` as the dataset index
    cur_image = all_data.get_image(idx)
    cur_label = all_data.get_label(idx)
    cur_class = all_data.get_class(cur_label)

    ax.title.set_text(cur_class)
    plt.axis('off')
    plt.imshow(cur_image)

"""## Model structure

Here's where you'll define the structure of your neural network. Refer back to earlier workshop notebooks for reference.
"""

import torch.nn as nn
import torch.nn.functional as F

class BirdModel(nn.Module):
    def __init__(self, num_classes=20):
        super(BirdModel, self).__init__()
        # input = 224 x 224 x 3

        self.conv1 = nn.Conv2d(3, 96, 5, 2)
        self.batchnorm1 = nn.BatchNorm2d(num_features=96)
        self.pool = nn.MaxPool2d(3, 2)
        self.conv2 = nn.Conv2d(96, 256, 5, 2)
        self.batchnorm2 = nn.BatchNorm2d(num_features=256)
        self.conv3 = nn.Conv2d(256, 384, 3, 1)
        self.conv4 = nn.Conv2d(384, 384, 3, 1)
        self.batchnorm3 = nn.BatchNorm2d(num_features=384)

        self.fc1 = nn.Linear(384*9*9, 4096)
        self.fc2 = nn.Linear(4096, num_classes)

        self.dropout = nn.Dropout(p=0.3)
    
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.batchnorm1(x)
        x = self.pool(F.relu(self.conv2(x)))
        x = self.dropout(x)
        x = self.batchnorm2(x)
        x = F.relu(self.conv3(x))
        x = self.batchnorm3(x)
        x = F.relu(self.conv4(x))
        x = self.pool(F.relu(self.conv4(x)))
        x = self.batchnorm3(x)

        x = x.view(-1, 384*9*9)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        return x

"""## Training setup

### Hyperparameters

Here's where we'll define our hyperparameters. We put them all in this cell for ease of readability; if you choose to add more hyperparameters, we suggest you add them here.

As you're tuning your model, change these values how you see fit!
"""

batch_size = 64
learning_rate = 0.0001
num_epochs = 30

"""### Data Augmentation

If you choose to use data augmentation, add your augmentation transforms here.
"""

aug = torchvision.transforms.Compose([
    torchvision.transforms.RandomHorizontalFlip(p=0.5),
    torchvision.transforms.RandomPerspective(distortion_scale=0.5, p=0.5)
])

"""### Data loaders

Here we'll create the data loaders for the train and validation set. To split `all_data` into the training and validation sets, read the PyTorch documentation for `random_split`: https://pytorch.org/docs/stable/data.html#torch.utils.data.random_split

Be sure to pass in the `batch_size` hyperparameter to the DataLoaders, and be sure to shuffle the training data loader!
"""

splitted = torch.utils.data.random_split(all_data, [2490, 623])

train_len = len(splitted[0])
val_len = len(splitted[1])

train_set, val_set = splitted[0], splitted[1]

train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=True)
val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=False)

"""## Training

It's time to train our model!

### Evaluation function

First, let's create a function that evaluates the accuracy of a model on a specified dataset. We provide some of the skeleton code, but you'll be coding this one on your own!

Be sure to call `.to(device=device)` on any data tensors to make sure PyTorch is using the GPU.
"""

# split is a variable you can set as the "name" of the dataset (either "train" or "val")
def evaluate(model, data_loader, name="val"):
    correct = 0  # number of correct predictions
    total = 0    # total number of examples in the data loader
    
    with torch.no_grad():
      for images, labels in data_loader:
        outputs = model(images.to(device=device).float())
        predicted = torch.argmax(outputs.data, 1)
        predicted = predicted.cpu()   # Move to cpu to be compared with labels, which are on cpu
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    print(f'Accuracy of the network on the {total} {name} images: {100 * correct / total}%')

"""### Training loop

This is it: this is where your model learns! You'll also be implementing this function on your own. A couple tips:
* Be sure to apply augmentations to your data if you're using them
* Be sure to call `.to(device=device)` on your model and any data tensors to make sure PyTorch is using the GPU
* Call `evaluate` on both the train and validation data loaders after each epoch
"""

torch.cuda.empty_cache()

model = BirdModel().to(device=device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), learning_rate)

start_time = time.time()
for epoch in range(num_epochs):

    epoch_loss = 0
    for batch_idx, (images, labels) in enumerate(train_loader):
      images = images.to(device=device)
      labels = labels.to(device=device) # Put the labels on GPU as well
      
      # Fill in the rest of the training loop
      optimizer.zero_grad()
      images = aug(images)
      images = images.float()
      outputs = model(images).squeeze()
      loss = criterion(outputs, labels)
      loss.backward()
      optimizer.step()

      epoch_loss += loss.item() / labels.shape[0]
      if batch_idx % 100 == 0:
        print(f"Epoch {epoch}, batch {batch_idx}: {loss}")

    evaluate(model, train_loader, name="train")
    evaluate(model, val_loader, name="val")

end_time = time.time()
print(f"Total training time: {end_time - start_time} sec")

"""### Saving model weights

Save your weights! Your final model's weights will be one component of your submission. We recommend saving weights with a recognizable name, such as the date and a short description of the structure of your model (e.g. `"2022_10_25_3LayerCNN"`)
"""

model_name = "2022_11_28_MultiLayerCNN"  

date_str = date.today().strftime("%Y_%m_%d")
model_weights_filename = f"{date_str}_{model_name}.pt"

torch.save(model.state_dict(), f"{model_weights_filename}")
print(f"Model weights saved as {model_weights_filename}")

"""### Refining your model

Now that you've trained a basic model, it's time to see if you can improve its accuracy. Feel free to change anything – the model structure, hyperparameters, augmentation – or try employing training strategies like regularization or early stopping. Get creative!

## Predict functions

These functions will let us run the test set through your model. It is **incredibly important** that you implement these functions!

`predict` should load the image at the specified path, run it through the model (variable provided as a parameter), and output the **predicted label** (the single numerical value between 0 and 19) – *not* the class name (e.g. the name of the bird).
"""

def load_model():
    model_path = "2022_11_28_MultiLayerCNN.pt"

    model = BirdModel().to(device)
    model.load_state_dict(torch.load(model_path))
    return model

def predict(model, image_path):
    prediction = None
    image = Image.open(image_path)
    image = transform(image) # ToTensor
    model = model.cuda() 
    output = model(image.to(device=device).unsqueeze(0).float()).cuda()
    prediction = torch.argmax(output.data, 1)
    prediction = prediction.cpu()   # Move to cpu to be compared with labels, which are on cpu | maybe we dont need this line
    return prediction

print(predict(load_model(), "bird_data/0 - BALTIMORE ORIOLE/0_35.jpg")) #label 0
print(predict(load_model(), "bird_data/2 - MYNA/2_119.jpg")) #label 2
print(predict(load_model(), "bird_data/3 - BARN OWL/3_34.jpg")) #label 3
print(predict(load_model(), "bird_data/15 - MAGPIE GOOSE/15_151.jpg")) #label 15 
print(predict(load_model(), "bird_data/16 - HOUSE FINCH/16_231.jpg")) #label 16