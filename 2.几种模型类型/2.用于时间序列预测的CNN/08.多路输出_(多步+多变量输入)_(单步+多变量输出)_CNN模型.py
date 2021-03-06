# multivariate output 1d cnn example
from numpy import array
from numpy import hstack
from keras.models import Model
from keras.layers import Input
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D

# split a multivariate sequence into samples
def split_sequences(sequences, n_steps):
	X, y = list(), list()
	for i in range(len(sequences)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the dataset
		if end_ix > len(sequences)-1:
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequences[i:end_ix, :], sequences[end_ix, :]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)

# define input sequence
in_seq1 = array([10, 20, 30, 40, 50, 60, 70, 80, 90])
in_seq2 = array([15, 25, 35, 45, 55, 65, 75, 85, 95])
out_seq = array([in_seq1[i]+in_seq2[i] for i in range(len(in_seq1))])
# convert to [rows, columns] structure
in_seq1 = in_seq1.reshape((len(in_seq1), 1))
in_seq2 = in_seq2.reshape((len(in_seq2), 1))
out_seq = out_seq.reshape((len(out_seq), 1))
# horizontally stack columns
dataset = hstack((in_seq1, in_seq2, out_seq))
# 定义时间步长
n_steps = 3
# 数据转换，获取输入输出对：X(6,3,3)y(6,3),具体调用的split_sequences函数见之前章节“多步+多变量入_单步+多变量出”文档
X, y = split_sequences(dataset, n_steps)
# 定义特征值数量
n_features = X.shape[2]
"""
将输出y
[[ 40  45  85]
 [ 50  55 105]
 [ 60  65 125]
 [ 70  75 145]
 [ 80  85 165]
 [ 90  95 185]]
 转换成三路输出
 [[40]
  [50]
  [60]
  [70]
  [80]
  [90]]
 和
 [[45]
  [55]
  [65]
  [75]
  [85]
  [95]]
 和
 [[ 85]
  [105]
  [125]
  [145]
  [165]
  [185]]
"""
# 将(6,3)转换成3个(6,1)
y1 = y[:, 0].reshape((y.shape[0], 1))
y2 = y[:, 1].reshape((y.shape[0], 1))
y3 = y[:, 2].reshape((y.shape[0], 1))

# 定义网络输入和隐藏层的形状，(None,3,3)，第一个None元素代表有N组数据
visible = Input(shape=(n_steps, n_features))
# 卷积层(None,3,3)->(None,2,64)
cnn = Conv1D(filters=64, kernel_size=2, activation='relu')(visible)
# 池化层(None,2,64)->(None,1,64)
cnn = MaxPooling1D(pool_size=2)(cnn)
# 平滑层(None,1,64)->(None,64)
cnn = Flatten()(cnn)
# 密集层(None,64)->(None,50)
cnn = Dense(50, activation='relu')(cnn)

# 定义多路输出的网络结构
# 密集层(None,50)->(None,1)
output1 = Dense(1)(cnn)
# 密集层(None,50)->(None,1)
output2 = Dense(1)(cnn)
# 密集层(None,50)->(None,1)
output3 = Dense(1)(cnn)

# 将输入结构，和三路输出结构定义到模型中
model = Model(inputs=visible, outputs=[output1, output2, output3])
model.compile(optimizer='adam', loss='mse')
model.fit(X, [y1,y2,y3], epochs=2000, verbose=0)

# 构造输入数据x_input形状(1,3,3)，来测试网络
x_input = array([[70,75,145], [80,85,165], [90,95,185]])
x_input = x_input.reshape((1, n_steps, n_features))
yhat = model.predict(x_input, verbose=0)
print(yhat)