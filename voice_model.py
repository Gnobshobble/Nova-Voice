# Neccessary Libraries
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader 
import os
import librosa
from torchvision import transforms

# Hyperparameters

# The dimensionality of the embedding vectors. 
# Larger values can capture more complex linguistic features but increase computational cost.
embedding_size = 256 
# The number of hidden units in the LSTM. 
# Larger values can capture more complex patterns but increase computational cost.
hidden_size = 512
# The number of LSTM layers. 
# More layers can capture longer-range dependencies but increase complexity.
num_layers = 4
# The probability of dropping neurons during training to prevent overfitting.
dropout = 0.1
# The number of iterations through the data set that the model should go through when training, 
# higher number of iterations means more accuracy but much longer training times, and can lead to overfitting.
epochs = 1
# Higher values of num_mels generally provide a more detailed representation of the audio signal, 
# which can lead to better quality generated speech. 
# However, it also increases the computational cost of the model.
num_mels = 80
reduction_factor = 0.8

# Define Attention Mechanism
class Attention(nn.Module):
    def __init__(self, hidden_size):
        super(Attention, self).__init__()
        # ... Implement attention layers ...
        self.attn = nn.Linear(hidden_size * 2, hidden_size)
        self.v = nn.Parameter(torch.rand(hidden_size))
    
    def forward(self, hidden, encoder_outputs):
        # ... Calculate attention weights and context vector ...
        seq_len = encoder_outputs.size(1)
        hidden = hidden.unsqueeze(1).repeat(1, seq_len, 1)
        
        energy = torch.tanh(self.attn(torch.cat((hidden, encoder_outputs), 2)))

        attention_weights = torch.sum(self.v * energy, dim=2)
        attention_weights = F.softmax(attention_weights, dim=1)
        
        context_vector = torch.bmm(attention_weights.unsqueeze(1), encoder_outputs)
        context_vector = context_vector.squeeze(1)
        
        return attention_weights, context_vector

attention = Attention(hidden_size)

# Define Postnet
class Postnet(nn.Module):
    def __init__(self, num_mels, hidden_size, num_layers):
        super(Postnet, self).__init__()
        # ... Implement postnet layers ...
        self.conv_layers = nn.ModuleList()
        for i in range(num_layers - 1):
            in_channels = num_mels if i == 0 else hidden_size
            self.conv_layers.append(
                nn.Sequential(
                    nn.Conv1d(in_channels, hidden_size, kernel_size=5, stride=1, padding=2),
                    nn.BatchNorm1d(hidden_size),
                    nn.Tanh()
                )
            )
        self.conv_layers.append(
        nn.Conv1d(hidden_size, num_mels, kernel_size=5, stride=1, padding=2)
        )

    def forward(self, mel_input):
        # ... Postnet processing ...
        x = mel_input
        for layer in self.conv_layers:
            x = layer(x)
        mel_output = x
        return mel_output


postnet = Postnet(num_mels, hidden_size, num_layers)

# Define encoder and decoder
class Decoder(nn.Module):
    def __init__(self, hidden_size, embedding_size, num_mels, dropout):
        super(Decoder, self).__init__()
        self.lstm = nn.LSTMCell(embedding_size + hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.linear_out = nn.Linear(hidden_size, int(num_mels * reduction_factor))

    def forward(self, input_embedding, hidden_state, cell_state, context_vector):
        # Combine input and context vector
        combined_input = torch.cat((input_embedding, context_vector), dim=1)

        # LSTM step
        hidden_state, cell_state = self.lstm(combined_input, (hidden_state, cell_state))
        hidden_state = self.dropout(hidden_state)

        # Output layer
        mel_output = self.linear_out(hidden_state)
        return mel_output, hidden_state, cell_state

class Encoder(nn.Module):
    def __init__(self, input_size, embedding_size, hidden_size, num_layers):   

        super(Encoder, self).__init__()
        self.embedding = nn.Embedding(input_size, embedding_size)
        self.lstm = nn.LSTM(embedding_size, hidden_size, num_layers, bidirectional=True)

    def forward(self, inputs):
        embedded = self.embedding(inputs)
        outputs, _ = self.lstm(embedded)
        return outputs

encoder = Encoder(50, embedding_size, hidden_size, num_layers)
decoder = Decoder(hidden_size, embedding_size, num_mels, dropout)

# Define the dataset class
class TTSDataset(Dataset):
    def __init__(self, text_paths, audio_paths):
        self.text_paths = sorted(os.listdir(text_paths))
        self.audio_paths = sorted(os.listdir(audio_paths))
        self.textdir = text_paths
        self.audiodir = audio_paths
        self.longest_entry_length = 0
        self.unique_words = set()

        # Determine the longest entry, build the unique word dictionary
        for text_file in self.text_paths:
            with open(os.path.join(self.textdir, text_file), 'r') as f:
                text = f.read().split()
                self.unique_words.update(text)
                if len(text) > self.longest_entry_length:
                    self.longest_entry_length = len(text)

        # Create a word-to-index dictionary
        self.word2idx = {word: idx for idx, word in enumerate(sorted(self.unique_words))}

    def __len__(self):
        return len(self.text_paths)

    def __getitem__(self, idx):
        text_path = os.path.join(self.textdir, self.text_paths[idx])
        audio_path = os.path.join(self.audiodir, self.audio_paths[idx])
        
        with open(text_path, 'r') as f:
            text = f.read().split()

        # Create a matrix
        text_matrix = torch.zeros((self.longest_entry_length, len(self.word2idx)), dtype=torch.float)

        # Fill matrix
        for i, word in enumerate(text):
            if i < self.longest_entry_length:
                word_idx = self.word2idx[word]
                text_matrix[i, word_idx] = 1.0  # Presence of word

        # Load and preprocess the audio
        audio, _ = librosa.load(audio_path, sr=22050)
        
        # print(text_matrix.shape)
        print(f'{audio.shape}')
        # print(audio)

        return text_matrix, torch.from_numpy(audio)

dataset = TTSDataset('/Users/rishabh/NovaVoice/Nova-Voice/data/text', '/Users/rishabh/NovaVoice/Nova-Voice/data/audio')

# Split your dataset into train and validation sets
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = torch.utils.data.random_split(dataset,   
 [train_size, val_size])

# Create data loaders
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# Define the model
# Given that you have defined the necessary components (encoder, decoder, attention, and postnet), 
# you can create a TTS model class to encapsulate them:

class Tacotron(nn.Module):
    def __init__(self, encoder, decoder, postnet, attention, num_mels):
        super(Tacotron, self).__init__()
        self.encoder = encoder # abstracts the data into a more efficient form to be train on
        self.decoder = decoder # converts the abstract data back to usable data
        self.postnet = postnet # a smaller model that is trained with the encoder/decoder (this is almost just another activation layer) that helps refine the mel spectrum quality after it comes back from the decoder
        self.attention = attention # a second smaller model (this is closer to a discriminator in a GAN) that relates the text to the audio 
        self.num_mels = num_mels

    def forward(self, text_input, mel_input):
        # Encoder
        encoder_outputs, _ = self.encoder(text_input)

        # Decoder
        # ... decoder logic with attention and postnet ...

        return mel_output


model = Tacotron(encoder, decoder, postnet, attention, num_mels)  

# Define the loss and optimizer functions
criterion = torch.nn.L1Loss()
optimizer = optim.Adam(model.parameters(), lr=0.001)  # Adjust learning rate as needed

# Create a training loop
for epoch in range(epochs):
    for i, (text_input, mel_target) in enumerate(train_loader):
        optimizer.zero_grad()
        mel_output = model(text_input, mel_target)
        loss = criterion(mel_output, mel_target)
        loss.backward()
        optimizer.step()