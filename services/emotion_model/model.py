import pandas as pd
import os 
import matplotlib.pyplot as plt
from tensorflow.python.keras.layers.core import Dropout
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Comment when using tensorflow!
# os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
# import keras


# Comment when using PlaidML!
from tensorflow import keras


epochs = 300
num_classes = 2

paths = {
    'alert_train': '../../dataset/alert_train.csv',
    'alert_test': '../../dataset/alert_test.csv',
    'non_vigilant_train': '../../dataset/non_vigilant_train.csv',
    'non_vigilant_test': '../../dataset/non_vigilant_test.csv',
    'tired_train': '../../dataset/tired_train.csv',
    'tired_test': '../../dataset/tired_test.csv'
}
df = {}


x_train = []
x_test = []
y_train = []
y_test = []

x_cols = ['anger','contempt','disgust','fear','happiness','neutral','sadness','surprise']
y_col = 'class'



for key, path in paths.items():
    df[key] = pd.read_csv(path)
    rows  = len(df[key].index)

    is_test = key.split("_")[-1] == 'test'

    x_arr = x_test if is_test else x_train
    y_arr = y_test if is_test else y_train

    
    for row in range(rows):
        # if df[key].iloc[row]['neutral'] >= 0.5 and not is_test:
        #     continue
        
        x_arr.append(
            [ df[key].iloc[row][col] / (10 if col == 'neutral' else 1) for col in x_cols]
        )
        y_arr.append(df[key].iloc[row][y_col])

    




print(f"Processed {len(x_train)} training samples!")
print(f"Processed {len(x_test)} testing samples!")



model = keras.Sequential([
    keras.layers.Input(shape=[len(x_cols)]),
    keras.layers.Dense(256, activation='relu'),    
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=3e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

model.summary()

hist = model.fit(
    x_train,
    y_train,
    shuffle=True,
    batch_size=256,
    epochs=epochs,
    validation_data=(x_test, y_test)
)
	
plt.title("Loss")
plt.plot(hist.history['loss'])
plt.show()
plt.title("Accuracy")
plt.plot(hist.history['accuracy'])
plt.show()
