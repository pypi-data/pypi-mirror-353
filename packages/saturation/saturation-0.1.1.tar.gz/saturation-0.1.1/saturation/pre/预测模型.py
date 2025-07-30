from keras.layers import Input, Dense, LSTM, Conv1D, Dropout, Bidirectional, Multiply, Flatten, Lambda, RepeatVector, Permute, Reshape
from keras.models import Model
from keras import backend as K
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from keras.models import load_model 
from sklearn.metrics import mean_squared_error, mean_absolute_error

SINGLE_ATTENTION_VECTOR = False
def attention_3d_block(inputs):
    # inputs.shape = (batch_size, time_steps, jiinput_dim)
    input_dim = int(inputs.shape[2])
    a = inputs
    #a = Permute((2, 1))(inputs)
    #a = Reshape((input_dim, TIME_STEPS))(a) # this line is not useful. It's just to know which dimension is what.
    a = Dense(input_dim, activation='softmax')(a)
    if SINGLE_ATTENTION_VECTOR:
        a = Lambda(lambda x: K.mean(x, axis=1), name='dim_reduction')(a)
        a = RepeatVector(input_dim)(a)
    a_probs = Permute((1, 2), name='attention_vec')(a)    #Permute是置换维度：1和2交换

    output_attention_mul = merge([inputs, a_probs], name='attention_mul', mode='mul')
    return output_attention_mul

# 注意力机制的另一种写法 适合上述报错使用 
def attention_3d_block2(inputs, single_attention_vector=False):
    # 如果上一层是LSTM，需要return_sequences=True
    # inputs.shape = (batch_size, time_steps, input_dim)
    time_steps = K.int_shape(inputs)[1]
    input_dim = K.int_shape(inputs)[2]
    
    a = Permute((2, 1))(inputs)
    a = Dense(time_steps, activation='softmax')(a)    #Dense全连接层
    if single_attention_vector:
        a = Lambda(lambda x: K.mean(x, axis=1))(a)
        a = RepeatVector(input_dim)(a)
        

    a_probs = Permute((2, 1))(a)
    # 乘上了attention权重，但是并没有求和，好像影响不大
    # 如果分类任务，进行Flatten展开就可以了
    # element-wise
    output_attention_mul = Multiply()([inputs, a_probs])  #点乘
    return output_attention_mul


#单步数据处理
def create_dataset(dataset, look_back):
    '''
    对数据进行处理
    '''
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back),:]
        dataX.append(a)
        dataY.append(dataset[i + look_back,:])
    TrainX = np.array(dataX)
    Train_Y = np.array(dataY)

    return TrainX, Train_Y

#两步数据处理
def create_dataset2(dataset, look_back):
    '''
    对数据进行处理
    '''
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-2):
        a = dataset[i:(i+look_back),:]
        dataX.append(a)
        dataY.append([dataset[i + look_back,:],dataset[i + look_back+1,:]])
    TrainX = np.array(dataX)
    Train_Y = np.array(dataY)

    return TrainX, Train_Y


#多维归一化  返回数据和最大最小值
def NormalizeMult(data):
    #normalize 用于反归一化
    data = np.array(data)
    normalize = np.arange(2*data.shape[1],dtype='float64')

    normalize = normalize.reshape(data.shape[1],2)
    #print(normalize.shape)
    for i in range(0,data.shape[1]):
        #第i列
        list = data[:,i]
        listlow,listhigh =  np.percentile(list, [0, 100])
        # print(i)
        normalize[i,0] = listlow
        normalize[i,1] = listhigh
        delta = listhigh - listlow
        if delta != 0:
            #第j行
            for j in range(0,data.shape[0]):
                data[j,i]  =  (data[j,i] - listlow)/delta
    #np.save("./normalize.npy",normalize)
    return  data,normalize

#多维反归一化
def FNormalizeMult(data,normalize):
    data = np.array(data)
    for i in  range(0,data.shape[1]):
        listlow =  normalize[i,0]
        listhigh = normalize[i,1]
        delta = listhigh - listlow
        if delta != 0:
            #第j行
            for j in range(0,data.shape[0]):
                data[j,i]  =  data[j,i]*delta + listlow

    return data


def attention_block_3(inputs):            
    feature_cnt=K.int_shape(inputs)[1]
    dim=K.int_shape(inputs)[2]
    h_block = int(feature_cnt*dim/64/2)
    hidden = Flatten()(inputs)
    while(h_block >= 1):
        h_dim = h_block * 64
        hidden = Dense(h_dim,activation='selu',use_bias=True)(hidden)
        h_block = int(h_block/2)
    attention = Dense(feature_cnt,activation='softmax',name='attention')(hidden)
#    attention = Lambda(lambda x:x*category)(attention)
    attention = RepeatVector(dim)(attention)
    attention = Permute((2, 1))(attention)
    
    attention_out = Multiply()([attention,inputs])
    return attention_out


def attention_block_4(inputs):   #求和
    feature_cnt=K.int_shape(inputs)[1]
    dim=K.int_shape(inputs)[2]
    a = Flatten()(inputs)
    a = Dense(feature_cnt*dim,activation='softmax')(a) 
    a = Reshape((feature_cnt,dim,))(a)
    a = Lambda(lambda x: K.sum(x, axis=2), name='attention')(a)
    a = RepeatVector(dim)(a)
    a_probs = Permute((2, 1), name='attention_vec')(a)
    attention_out = Multiply()([inputs, a_probs])
    return attention_out

def attention_model():
    inputs = Input(shape=(TIME_STEPS, INPUT_DIMS))
    x = Conv1D(filters=64, kernel_size=1, activation='relu')(inputs)
    x = Dropout(0.3)(x)
    lstm_out = Bidirectional(LSTM(lstm_units, return_sequences=True))(x)
    lstm_out = Dropout(0.3)(lstm_out)
    attention_mul = attention_block_4(lstm_out)
    attention_mul = Flatten()(attention_mul)
    output = Dense(1, activation='sigmoid')(attention_mul)
    model = Model(inputs=[inputs], outputs=output)
    return model


def bp():
    inputs = Input(shape=(TIME_STEPS, INPUT_DIMS))
    x=Dense(128, activation='relu')(inputs)
    x = Dropout(0.3)(x)
    x=Dense(64,activation='relu')(x)
    x = Dropout(0.3)(x)
    x=Dense(32,activation='relu')(x)
    x = Flatten()(x)
    output = Dense(2, activation='sigmoid')(x)
    model = Model(inputs=[inputs], outputs=output)
    return model
    

def attention_model1():
    inputs = Input(shape=(TIME_STEPS, INPUT_DIMS))

    x = Conv1D(filters = 64, kernel_size = 1, activation = 'relu')(inputs)  #, padding = 'same'
    x = Dropout(0.3)(x)

    #lstm_out = Bidirectional(LSTM(lstm_units, activation='relu'), name='bilstm')(x)
    #对于GPU可以使用CuDNNLSTM
    lstm_out = Bidirectional(LSTM(lstm_units, return_sequences=True))(x)
    lstm_out = Dropout(0.3)(lstm_out)
    attention_mul = attention_block_3(lstm_out)
    attention_mul = Flatten()(attention_mul)
    
    attention_mul = Dense(128, activation='sigmoid')(attention_mul)
    attention_mul = Dropout(0.3)(attention_mul)
   
    output = Dense(2, activation='sigmoid')(attention_mul)
    model = Model(inputs=[inputs], outputs=output)
    return model

def lstm_attention_model():
    inputs = Input(shape=(TIME_STEPS, 1))
    x = LSTM(units=128, return_sequences=True)(inputs)
    x = LSTM(units=64)(x)
    output = Dense(2, activation='sigmoid')(x)
    model = Model(inputs=[inputs], outputs=output)
    return model


def cnn1_model():
    inputs = Input(shape=(TIME_STEPS, INPUT_DIMS))
    x=Reshape((INPUT_DIMS, TIME_STEPS), input_shape=(TIME_STEPS, INPUT_DIMS))(inputs)
    x=Conv1D(64, 2, activation='relu', input_shape=(INPUT_DIMS, 1))(x)
    x = Dropout(0.3)(x)
    x=Conv1D(32, 2, activation='relu', input_shape=(INPUT_DIMS, 1))(x)
    #x=attention_block_3(x)
    x = Flatten()(x)
    output=Dense(2, activation='sigmoid')(x)
    model = Model(inputs=[inputs], outputs=output)
    return model

def mean_absolute_percentage_error(y_true, y_pred): 
    # 计算MAPE
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # 避免除以零的情况
    non_zero = y_true != 0
    mape = np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100
    return mape

#加载数据
data=pd.read_excel(r"E:\魏铨\实验结果\etc\下行\flow-kehuo-adjusted.xlsx")
data=data[['flow','etc_flow','etc_ke','etc_huo','inner','outer']]
g1=max(data['flow'])
g2=min(data['flow'])

data= (data - data.min()) / (data.max() - data.min())

train=data.iloc[:200,:]
train=train.values
test=data.iloc[201:,:]
test=test.values

INPUT_DIMS = 6
TIME_STEPS = 5
lstm_units = 64



train_data = train[:,0].reshape(len(train),1)


test_data = test[:,0].reshape(len(test),1)

#构建train数据集
train_X, _ = create_dataset2(train,TIME_STEPS)
_ , train_Y = create_dataset2(train_data,TIME_STEPS)
train_Y=train_Y.reshape(train_Y.shape[0],2)
#构建test数据集
test_X, _ = create_dataset2(test,TIME_STEPS)
_ , test_Y = create_dataset2(test_data,TIME_STEPS)
test_Y=test_Y.reshape(test_Y.shape[0],2)

model = attention_model1()
model.compile(optimizer='adam', loss='mse', run_eagerly=True)
model.summary()
model.fit(train_X, train_Y, batch_size=64,epochs=100,validation_split=0.1) #600
# 保存模型到指定路径
model.save(r"E:\魏铨\实验结果\etc\下行\model_all.h5")
#model.save(r"E:\魏铨\实验结果\etc\下行\model_ke1.h5")
#model = load_model(r"E:\魏铨\实验结果\etc\下行\model_huo1.h5")
y=test_Y
t=model.predict(test_X)
y = y * (g1 - g2) + g2
t = t* (g1 - g2) + g2
# 绘制预测结果和实际数据
plt.figure(figsize=(10, 6))  # 设置图表大小
plt.plot(y[:,0], label='Estimated Data', color='blue', marker='o')  # 实际数据
plt.plot(t[:,0], label='Predicted Data', color='red', linestyle='--', marker='x')  # 预测数据

# 添加图例
plt.legend()

# 添加标题和轴标签
plt.title('Comparison of Estimated and Predicted Data')
plt.xlabel('Time Step')
plt.ylabel('Value')

# 显示图表
plt.show()

# 计算 RMSE
rmse = mean_squared_error(y[:, 1], t[:, 1], squared=False)
print("RMSE:", rmse)

# 计算 MAE
mae = mean_absolute_error(y[:, 1], t[:, 1])
print("MAE:", mae)

# 计算 MAPE
mape = mean_absolute_percentage_error(y[:, 1], t[:, 1])
print("MAPE: {:.2f}%".format(mape))