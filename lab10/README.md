这个 lab 是写 OpenMP 利用多线程加速代码段。
OpenMP 全称是  Open specification for Multi-Processing。

## 向量加法的加速

首先， 这样写肯定是错了：

```c
void v_add_naive(double* x, double* y, double* z) 
{
	#pragma omp parallel
	{
		for(int i = 0; i < ARRAY_SIZE; i++)
        {
			z[i] = x[i] + y[i];
        }
	}
}
```
这样写的话， 相当于每个线程都从左到右完整加了一遍。

可以写成这样：第 i 个线程计算 mod num_of_thread 为 i 的部分。

```c
// Edit this function (Method 1) 
void v_add_optimized_adjacent(double* x, double* y, double* z) 
{
	#pragma omp parallel 
	{
        int num_thread = omp_get_num_threads();
        // 注意：这个 omp_get_num_threads 应该在并行区域内部调用
        // 否则返回的是 1
		int thread_id = omp_get_thread_num();
		for(int i = thread_id; i < ARRAY_SIZE; i += num_thread)
		{
			z[i] = x[i] + y[i];
		}
        // 虽然这种方法确保了工作的平等分配，但它可能不是最优的
        //特别是在处理器缓存利用和内存访问模式方面。
	}
}
```

实际上，好心的 OpenMP 开发者为我们提供了快捷方式， 实现类似上述 slicing 的效果， 叫做 `#pragma omp parallel for`:

```c
void v_add_naive(double* x, double* y, double* z) 
{
	#pragma omp parallel for
	{
		for(int i = 0; i < ARRAY_SIZE; i++)
		{
			z[i] = x[i] + y[i];
		}
	}
}
```

另外， 我还可以采用分块的策略：

```c
// Edit this function (Method 2) 
void v_add_optimized_chunks(double* x, double* y, double* z) 
{
    #pragma omp parallel
    {
        int num_thread = omp_get_num_threads();
        int thread_id = omp_get_thread_num();
        int chunk_size = ARRAY_SIZE / num_thread;
        int start = thread_id * chunk_size;
        int end = (thread_id == num_thread - 1) ? ARRAY_SIZE : start + chunk_size;
        for (int i = start; i < end; i++) 
		{
            z[i] = x[i] + y[i];
        }
    }
}
```


最后来看看结果：

+ `ARRAY_SIZE = 10000000`

```shell
Naive: took 0.139890 seconds
Optimized adjacent
Optimized adjacent: 1 thread(s) took 0.161176 seconds
Optimized adjacent: 2 thread(s) took 0.209880 seconds
Optimized adjacent: 3 thread(s) took 0.209149 seconds
Optimized adjacent: 4 thread(s) took 0.213102 seconds
Optimized adjacent: 5 thread(s) took 0.194082 seconds
Optimized adjacent: 6 thread(s) took 0.249398 seconds
Optimized adjacent: 7 thread(s) took 0.285246 seconds
Optimized adjacent: 8 thread(s) took 0.276469 seconds
Optimized adjacent: 9 thread(s) took 0.262148 seconds
Optimized adjacent: 10 thread(s) took 0.248477 seconds
Optimized adjacent: 11 thread(s) took 0.271849 seconds
Optimized adjacent: 12 thread(s) took 0.268224 seconds
Optimized adjacent: 13 thread(s) took 0.257311 seconds
Optimized adjacent: 14 thread(s) took 0.268496 seconds
Optimized adjacent: 15 thread(s) took 0.274083 seconds
Optimized adjacent: 16 thread(s) took 0.309585 seconds
Optimized adjacent: 17 thread(s) took 0.296942 seconds
Optimized adjacent: 18 thread(s) took 0.308666 seconds
Optimized adjacent: 19 thread(s) took 0.386265 seconds
Optimized adjacent: 20 thread(s) took 0.515873 seconds
Optimized chunks: 1 thread(s) took 0.130257 seconds
Optimized chunks: 2 thread(s) took 0.092258 seconds
Optimized chunks: 3 thread(s) took 0.075548 seconds
Optimized chunks: 4 thread(s) took 0.072534 seconds
Optimized chunks: 5 thread(s) took 0.069805 seconds
Optimized chunks: 6 thread(s) took 0.084975 seconds
Optimized chunks: 7 thread(s) took 0.081930 seconds
Optimized chunks: 8 thread(s) took 0.086473 seconds
Optimized chunks: 9 thread(s) took 0.081433 seconds
Optimized chunks: 10 thread(s) took 0.080054 seconds
Optimized chunks: 11 thread(s) took 0.070482 seconds
Optimized chunks: 12 thread(s) took 0.069111 seconds
Optimized chunks: 13 thread(s) took 0.071666 seconds
Optimized chunks: 14 thread(s) took 0.070125 seconds
Optimized chunks: 15 thread(s) took 0.072366 seconds
Optimized chunks: 16 thread(s) took 0.072359 seconds
Optimized chunks: 17 thread(s) took 0.067502 seconds
Optimized chunks: 18 thread(s) took 0.087893 seconds
Optimized chunks: 19 thread(s) took 0.089979 seconds
Optimized chunks: 20 thread(s) took 0.097394 seconds
```

可以看出， 效果最好的是分块策略， 其次是朴素策略（不加 OpenMP）, 最差是 splice 策略。然后 splice 策略是线程越多越慢， 感觉应该和缓存命中率有关， 缓存估计一直打不中。 分块策略线程越多基本是越快， 3~17 个线程数之间都很快。

还可以测下更大的数据看看：(最大线程数设为了 5， 因为 10 和 20 都跑不了， 中途会被 kill)

+ `ARRAY_SIZE = 100000000`

```shell
Naive
Naive: took 1.557364 seconds
Optimized adjacent
Optimized adjacent: 1 thread(s) took 1.774735 seconds
Optimized adjacent: 2 thread(s) took 1.978347 seconds
Optimized adjacent: 3 thread(s) took 2.530736 seconds
Optimized adjacent: 4 thread(s) took 2.820710 seconds
Optimized adjacent: 5 thread(s) took 3.265157 seconds
Optimized chunks: 1 thread(s) took 1.603984 seconds
Optimized chunks: 2 thread(s) took 0.988075 seconds
Optimized chunks: 3 thread(s) took 0.788707 seconds
Optimized chunks: 4 thread(s) took 0.719338 seconds
Killed
```

可以看出分块策略明显要快， 主要是缓存打中的比较多吧。 然后第二是朴素， 第三是 slicing。 slicing 依然是线程数越多越慢， 分块策略线程数越多越快。 但是好像也没比直接算快多少， 毕竟还要有线程调度的开销（context switch之类的）

## 向量内积的加速

这部分就是写一个向量内积的并行加速。 首先， 最朴素的办法是这样写：

```c
double dotp_naive(double* x, double* y, int arr_size) 
{
  double global_sum = 0.0;
  #pragma omp parallel
  {
    #pragma omp for
    for (int i = 0; i < arr_size; i++)
    {
      #pragma omp critical
      global_sum += x[i] * y[i];
    }
  }
  return global_sum;
}
```

相当于强制把 `global_sum += x[i] * y[i];` 串行化了。

然后我为了减少串行， 我可以让大家分别算， 算完了再加上去：

``` c
// EDIT THIS FUNCTION PART 1
// EDIT THIS FUNCTION PART 1
double dotp_manual_optimized(double* x, double* y, int arr_size) 
{
  double global_sum = 0.0;
  #pragma omp parallel
  {
    double temp = 0;
    #pragma omp for
    for (int i = 0; i < arr_size; i++)
    {
      temp += x[i] * y[i];
    }
    #pragma omp critical
    global_sum += temp;
  }
  return global_sum;
}
```

然后好心的 OpenMP 开发者还写了个 reduction 功能， 可以自动优化上述过程：

```c
// EDIT THIS FUNCTION PART 2
double dotp_reduction_optimized(double* x, double* y, int arr_size) {
    double global_sum = 0.0;
    #pragma omp parallel for reduction(+:global_sum)
    for (int i = 0; i < arr_size; i++)
    {
        global_sum += x[i] * y[i];
    }
    return global_sum;
}
```

运行时间如下：（N = 1000000）

```shell
Naive: 1 thread(s) took 1.196824 seconds
Manual Optimized: 1 thread(s) took 0.192061 seconds
Manual Optimized: 2 thread(s) took 0.099933 seconds
Manual Optimized: 3 thread(s) took 0.071019 seconds
Manual Optimized: 4 thread(s) took 0.048613 seconds
Manual Optimized: 5 thread(s) took 0.039362 seconds
Manual Optimized: 6 thread(s) took 0.035191 seconds
Manual Optimized: 7 thread(s) took 0.060881 seconds
Manual Optimized: 8 thread(s) took 0.054290 seconds
Manual Optimized: 9 thread(s) took 0.053337 seconds
Manual Optimized: 10 thread(s) took 0.053003 seconds
Manual Optimized: 11 thread(s) took 0.060889 seconds
Manual Optimized: 12 thread(s) took 0.047289 seconds
Manual Optimized: 13 thread(s) took 0.043915 seconds
Manual Optimized: 14 thread(s) took 0.043734 seconds
Manual Optimized: 15 thread(s) took 0.036913 seconds
Manual Optimized: 16 thread(s) took 0.034069 seconds
Manual Optimized: 17 thread(s) took 0.039366 seconds
Manual Optimized: 18 thread(s) took 0.039700 seconds
Manual Optimized: 19 thread(s) took 0.167410 seconds
Manual Optimized: 20 thread(s) took 0.096477 seconds
Reduction Optimized: 1 thread(s) took 0.200741 seconds
Reduction Optimized: 2 thread(s) took 0.101452 seconds
Reduction Optimized: 3 thread(s) took 0.067671 seconds
Reduction Optimized: 4 thread(s) took 0.049364 seconds
Reduction Optimized: 5 thread(s) took 0.043481 seconds
Reduction Optimized: 6 thread(s) took 0.042115 seconds
Reduction Optimized: 7 thread(s) took 0.065616 seconds
Reduction Optimized: 8 thread(s) took 0.101931 seconds
Reduction Optimized: 9 thread(s) took 0.060883 seconds
Reduction Optimized: 10 thread(s) took 0.047658 seconds
Reduction Optimized: 11 thread(s) took 0.044617 seconds
Reduction Optimized: 12 thread(s) took 0.045724 seconds
Reduction Optimized: 13 thread(s) took 0.059629 seconds
Reduction Optimized: 14 thread(s) took 0.048911 seconds
Reduction Optimized: 15 thread(s) took 0.055869 seconds
Reduction Optimized: 16 thread(s) took 0.045621 seconds
Reduction Optimized: 17 thread(s) took 0.047263 seconds
Reduction Optimized: 18 thread(s) took 0.041167 seconds
Reduction Optimized: 19 thread(s) took 0.048805 seconds
Reduction Optimized: 20 thread(s) took 0.262033 seconds
```

可以看出， 加速之后比朴素方法快了接近 12 倍，Manual 和 reduction 的效果差别也不大。 然后 Manual 和 reduction 都是线程数适中的时候最快。

下面的是 N = 10000000：

```shell
Naive: 1 thread(s) took 11.996685 seconds
Manual Optimized: 1 thread(s) took 1.999929 seconds
Manual Optimized: 2 thread(s) took 1.016785 seconds
Manual Optimized: 3 thread(s) took 0.724818 seconds
Manual Optimized: 4 thread(s) took 0.549912 seconds
Manual Optimized: 5 thread(s) took 0.516332 seconds
Manual Optimized: 6 thread(s) took 0.540431 seconds
Manual Optimized: 7 thread(s) took 0.605532 seconds
Manual Optimized: 8 thread(s) took 0.553323 seconds
Manual Optimized: 9 thread(s) took 0.523046 seconds
Manual Optimized: 10 thread(s) took 0.491000 seconds
Manual Optimized: 11 thread(s) took 0.458912 seconds
Manual Optimized: 12 thread(s) took 0.430009 seconds
Manual Optimized: 13 thread(s) took 0.418717 seconds
Manual Optimized: 14 thread(s) took 0.395745 seconds
Manual Optimized: 15 thread(s) took 0.383247 seconds
Manual Optimized: 16 thread(s) took 0.374074 seconds
Manual Optimized: 17 thread(s) took 0.360222 seconds
Manual Optimized: 18 thread(s) took 0.341138 seconds
Manual Optimized: 19 thread(s) took 0.421536 seconds
Manual Optimized: 20 thread(s) took 0.496320 seconds
Reduction Optimized: 1 thread(s) took 2.023310 seconds
Reduction Optimized: 2 thread(s) took 1.032524 seconds
Reduction Optimized: 3 thread(s) took 0.699379 seconds
Reduction Optimized: 4 thread(s) took 0.548186 seconds
Reduction Optimized: 5 thread(s) took 0.542051 seconds
Reduction Optimized: 6 thread(s) took 0.552382 seconds
Reduction Optimized: 7 thread(s) took 0.572134 seconds
Reduction Optimized: 8 thread(s) took 0.542383 seconds
Reduction Optimized: 9 thread(s) took 0.519548 seconds
Reduction Optimized: 10 thread(s) took 0.456110 seconds
Reduction Optimized: 11 thread(s) took 0.445125 seconds
Reduction Optimized: 12 thread(s) took 0.411311 seconds
Reduction Optimized: 13 thread(s) took 0.396156 seconds
Reduction Optimized: 14 thread(s) took 0.376057 seconds
Reduction Optimized: 15 thread(s) took 0.373362 seconds
Reduction Optimized: 16 thread(s) took 0.359459 seconds
Reduction Optimized: 17 thread(s) took 0.359522 seconds
Reduction Optimized: 18 thread(s) took 0.367128 seconds
Reduction Optimized: 19 thread(s) took 0.366627 seconds
Reduction Optimized: 20 thread(s) took 0.443391 seconds
```

这个效果看起来更显著了， 直接加速了接近 35 倍！！
然后 Manual 和 Reduction 的差距依然不大， 此时线程数越多基本上趋势是越快。（可能数据够大， 线程数增大而引起的缓存命中率下降被冲淡了）

## 性能分析

如何分析程序运行的时间？
+ gprof
GNU自带的工具， 不过主要是分析单线程程序的， 多线程程序用它可能不好用
+ 手写时钟
比如

```c
double start_time = omp_get_wtime();  // 获取开始时间

    #pragma omp parallel
    {
        int thread_ID = omp_get_thread_num();
        printf("Hello world from thread %d\n", thread_ID);
    }

    double end_time = omp_get_wtime();    // 获取结束时间
    double time_taken = end_time - start_time;  // 计算时间差

    printf("Time taken: %f seconds\n", time_taken);
```