import pandas as pd

"""
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
"""
import matplotlib.pyplot as plt

from numpy import vstack, ones
from numpy.linalg import lstsq

# Load the dataset (replace this with your actual dataset)
data = pd.read_csv("tt_times_results.csv")
data = data.loc[data["result"] != 0.0]

# Feature engineering (compute additional features if needed)
data["time_difference"] = data["white_seconds"] - data["black_seconds"]

data.sort_values(by=["time_difference"], inplace=True)


def best_fit_y_vals(x_values, y_values):
    """Get the slope and intercept that best fits the x and y values."""
    # y = mx + c
    x_matrix = vstack([x_values, ones(len(x_values))]).T
    return lstsq(x_matrix, y_values, rcond=None)[0]


slope, intercept = best_fit_y_vals(data["time_difference"], data["result"])
print(slope, intercept)
y_estimate = []
x_plot = []
x_val = data["time_difference"].min()
while x_val < data["time_difference"].max():
    x_plot.append(x_val)
    if slope * x_val + intercept < -1:
        y_estimate.append(-1)
    elif slope * x_val + intercept > 1:
        y_estimate.append(1)
    else:
        y_estimate.append(slope * x_val + intercept)

    x_val += 0.1


y_smooth = []
for i in range(0, len(y_estimate)):
    y_smooth.append(
        sum(y_estimate[max(0, i - 100) : min(len(y_estimate), i + 100)])
        / len(y_estimate[max(0, i - 100) : min(len(y_estimate), i + 100)])
    )


plt.plot(x_plot, y_smooth)
plt.show()

"""
# Split data into features (X) and target variable (y)
X = data[['time_difference']]
y = data['result']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# Train a logistic regression model
model = LogisticRegression(activation='tanh')
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print('Accuracy:', accuracy)

values_to_predict = []
for i in range(-60, 61, 1):
    values_to_predict.append([i])


pred_things = model.predict(values_to_predict)
print(values_to_predict)
print(pred_things)
"""
