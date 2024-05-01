import re
import matplotlib.pyplot as plt

def extract_data(file):
    with open(file, 'r') as f:
        data = f.read()

    # 使用正则表达式匹配所有数字和对应的线程数
    matches = re.findall(r'(?:Naive|Optimized (?:adjacent|chunks)): (\d+) thread\(s\) took (\d+\.\d+) seconds', data)
    
    # 分别存储线程数、秒数和优化方式
    thread_count = []
    seconds = []
    optimization_method = []
    
    for match in matches:
        thread_count.append(int(match[0]))
        seconds.append(float(match[1]))
        if "adjacent" in match[0]:
            optimization_method.append("adjacent")
        elif "chunks" in match[0]:
            optimization_method.append("chunks")
        else:
            optimization_method.append("naive")
    
    return thread_count, seconds, optimization_method

def plot(file):
    thread_count, seconds, optimization_method = extract_data(file)

    # 绘图
    plt.figure(figsize=(10, 6))

    # 绘制优化方式为 "adjacent" 的数据
    plt.scatter(thread_count[:20], seconds[:20], color='blue', label='Optimized adjacent')
    # 绘制优化方式为 "chunks" 的数据
    plt.scatter(thread_count[20:], seconds[20:], color='red', label='Optimized chunks')

    plt.xlabel('Thread count')
    plt.ylabel('Seconds')
    plt.title('Optimization Performance')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    plot('data.txt')