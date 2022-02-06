
#------------------------------------------------------------------------------
#* Linear Regression #2
#* 입력변수가 2개 이상
#------------------------------------------------------------------------------
import numpy as np

def derivative(f, var):
    if var.ndim == 1:  # vector

        temp_var = var

        delta = 1e-5
        diff_val = np.zeros(var.shape)

        for index in range(len(var)):
            target_var = float(temp_var[index])
            temp_var[index] = target_var + delta
            func_val_plust_delta = f(temp_var)
            temp_var[index] = target_var - delta
            func_val_minus_delta = f(temp_var)
            diff_val[index] = (func_val_plust_delta - func_val_minus_delta) / (2 * delta)
            temp_var[index] = target_var
        return diff_val

    elif var.ndim == 2:  # matrix
        temp_var = var
        delta = 1e-5
        diff_val = np.zeros(var.shape)

        rows = var.shape[0]
        columns = var.shape[1]

        for row in range(rows):

            for column in range(columns):
                target_var = float(temp_var[row, column])
                temp_var[row, column] = target_var + delta
                func_val_plus_delta = f(temp_var)
                temp_var[row, column] = target_var - delta
                func_val_minus_delta = f(temp_var)
                diff_val[row, column] = (func_val_plus_delta - func_val_minus_delta) / (2 * delta)
                temp_var[row, column] = target_var

        return diff_val

def loss_func(x, t):
    y = np.dot(x, W) + b

    return(np.sum((t-y)**2)) / (len(x))

def loss_val(x, t):
    y = np.dot(x, W) + b
    return (np.sum((t - y) ** 2)) / (len(x))

def predict(x):
    y = np.dot(x, W) + b

    return y



loaded_data = np.loadtxt('./CH05_data-01.csv', delimiter=',', dtype=np.float32)



x_data  = loaded_data[:, 0:-1]
t_data  = loaded_data[:, [-1]]
#데이터 차원 및 shape 확인
print("x_data.ndim = ", x_data.ndim, ", x_data.shape = ", x_data.shape)
print("t_data.ndim = ", t_data.ndim, ", t_data.shape = ", t_data.shape)



W = np.random.rand(3,1) #가중치 W 초기화
b = np.random.rand(1) #바이어스 b 초기화

print("W = ", W, ", W.shape = ", W.shape, ", b = ", b, ", b.shape = ", b.shape)




learning_rate = 1e-5

f = lambda x : loss_func(x_data, t_data)
print("Initial loss value = ", loss_val(x_data, t_data), "Initial W = ", W, "\n", ", b = ", b)

for step in range(30001):

    W -= learning_rate * derivative(f, W)  # 미분값이 거의 0이 되면 더 이상 변화가 없네.... ok....................
    b -= learning_rate * derivative(f, b)

    if (step % 3000 == 0):
        print("step = ", step, "loss value = ", loss_val(x_data, t_data), "W = ", W, ", b = ", b)


test_data = np.array([100, 98, 81])
ret = predict(test_data)
print("*** predict *** :", ret)
