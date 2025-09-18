import torch # Pytorch module 
import torch.nn as nn # for creating  neural networks
from torch.utils.data import DataLoader # For loading datasets in batches 
import torch.nn.functional as F # Functional module for loss and activation functions
import torchvision.transforms as transforms # For preprocessing and data augmentation
import logging  # Standard logging module

# Configure logging format and level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# for calculating the accuracy
def accuracy(outputs, labels):
    """
    Computes the accuracy by comparing predicted and actual labels.
    """
    _, preds = torch.max(outputs, dim=1)
    return torch.tensor(torch.sum(preds == labels).item() / len(preds))


# base class for the model
class ImageClassificationBase(nn.Module):
    """
    Base class providing common training and validation steps for image classification models.
    """
    def training_step(self, batch):
        """
        Performs a forward pass and computes the training loss.
        """
        images, labels = batch
        out = self(images)                  # Generate predictions
        loss = F.cross_entropy(out, labels) # Calculate loss
        logging.debug(f"Training step completed with loss: {loss.item():.4f}")
        return loss
    
    def validation_step(self, batch):
        """
        Evaluates the model on the validation batch.
        Returns loss and accuracy.
        """
        images, labels = batch
        out = self(images)                   # Generate prediction
        loss = F.cross_entropy(out, labels)  # Calculate loss
        acc = accuracy(out, labels)          # Calculate accuracy
        logging.debug(f"Validation step - Loss: {loss.item():.4f}, Accuracy: {acc.item():.4f}")
        return {"val_loss": loss.detach(), "val_accuracy": acc}
    
    def validation_epoch_end(self, outputs):
        """
        Aggregates validation loss and accuracy across all batches.
        """
        batch_losses = [x["val_loss"] for x in outputs]
        batch_accuracy = [x["val_accuracy"] for x in outputs]
        epoch_loss = torch.stack(batch_losses).mean()       # Combine loss  
        epoch_accuracy = torch.stack(batch_accuracy).mean()
        logging.info(f"Validation - Epoch Loss: {epoch_loss:.4f}, Accuracy: {epoch_accuracy:.4f}")
        return {"val_loss": epoch_loss, "val_accuracy": epoch_accuracy} # Combine accuracies
    
    def epoch_end(self, epoch, result):
        """
        Logs the metrics at the end of each epoch.
        """
        logging.info(
            f"Epoch [{epoch}], Last LR: {result['lrs'][-1]:.5f}, "
            f"Train Loss: {result['train_loss']:.4f}, "
            f"Validation Loss: {result['val_loss']:.4f}, "
            f"Validation Accuracy: {result['val_accuracy']:.4f}"
        )
        

# convolution block with BatchNormalization
def ConvBlock(in_channels, out_channels, pool=False):
    """
    Returns a convolutional block with optional max pooling.
    """
    layers = [
        nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True)
    ]
    if pool:
        layers.append(nn.MaxPool2d(4))
    return nn.Sequential(*layers)

class ResNet9(ImageClassificationBase):
    """
    A simplified ResNet-9 architecture with residual connections.
    Suitable for classification tasks.
    """
    def __init__(self, in_channels, num_diseases):
        super().__init__()
        # Initial convolutional layers
        self.conv1 = ConvBlock(in_channels, 64)
        self.conv2 = ConvBlock(64, 128, pool=True) # out_dim : 128 x 64 x 64 
        
        # First residual block
        self.res1 = nn.Sequential(
            ConvBlock(128, 128), 
            ConvBlock(128, 128)
        )

        # Deeper convolutional layers
        self.conv3 = ConvBlock(128, 256, pool=True) # out_dim : 256 x 16 x 16
        self.conv4 = ConvBlock(256, 512, pool=True) # out_dim : 512 x 4 x 44
        
        # Second residual block
        self.res2 = nn.Sequential(
            ConvBlock(512, 512), 
            ConvBlock(512, 512)
        )

        # Final classification layer
        self.classifier = nn.Sequential(
            nn.MaxPool2d(4),
            nn.Flatten(),
            nn.Linear(512, num_diseases)
        )
        
    def forward(self, xb): # xb is the loaded batch
        """
        Defines the forward pass of the network.
        """
        out = self.conv1(xb)
        out = self.conv2(out)
        out = self.res1(out) + out # Residual connection

        out = self.conv3(out)
        out = self.conv4(out)
        out = self.res2(out) + out # Residual connection
        
        out = self.classifier(out)
        return out   