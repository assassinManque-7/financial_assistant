import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

model = Sequential([Dense(4, input_shape = (10, ), activation = "relu")])
model.compile(optimizer = 'adam', loss = 'mse')
print("all good : ", model.summary())