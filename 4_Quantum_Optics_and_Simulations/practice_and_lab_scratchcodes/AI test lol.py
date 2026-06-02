import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Generate synthetic data for training
np.random.seed(0)
X = np.random.randint(1, 100, size=(1000, 2))  # 1000 pairs of random numbers between 1 and 9
y = X[:, 0] * X[:, 1]  # Calculate the true products

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Create and train the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate model performance
from sklearn.metrics import mean_squared_error
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Visualize Training Data and Model Fit
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap='viridis', alpha=0.5)
plt.title('Training Data and Model Fit')
plt.xlabel('Number 1')
plt.ylabel('Number 2')
plt.colorbar(label='Product')

# Create a meshgrid for plotting the regression surface
x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1
x1_range = np.arange(x1_min, x1_max, 1)
x2_range = np.arange(x2_min, x2_max, 1)
x1_grid, x2_grid = np.meshgrid(x1_range, x2_range)
X_plot = np.c_[x1_grid.ravel(), x2_grid.ravel()]

# Predict the product for the meshgrid
y_plot = model.predict(X_plot)
y_plot = y_plot.reshape(x1_grid.shape)

# Plot the regression surface
plt.subplot(1, 2, 2)
plt.contourf(x1_grid, x2_grid, y_plot, cmap='viridis', alpha=0.7)
plt.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap='viridis', edgecolors='k')
plt.title('Model Prediction on Test Data')
plt.xlabel('Number 1')
plt.ylabel('Number 2')
plt.colorbar(label='Product')





# Example Prediction
new_numbers = np.array([[2, 4]])
predicted_product = model.predict(new_numbers)
print(f"Predicted product of {new_numbers[0]} is: {predicted_product[0]}")

plt.tight_layout()
plt.show()