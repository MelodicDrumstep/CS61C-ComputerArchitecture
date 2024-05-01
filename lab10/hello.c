#include <stdio.h>
#include <omp.h>

int main() {

	printf("With OpenMP\n");

    double start_time = omp_get_wtime();  // 获取开始时间

    #pragma omp parallel
    {
        int thread_ID = omp_get_thread_num();
        printf("Hello world from thread %d\n", thread_ID);
    }

    double end_time = omp_get_wtime();    // 获取结束时间
    double time_taken = end_time - start_time;  // 计算时间差

    printf("Time taken: %f seconds\n", time_taken);

	start_time = omp_get_wtime();  // 获取开始时间

	printf("Without OpenMP\n");

    for(int i = 0; i < 20; i++)
    {
        int thread_ID = omp_get_thread_num();
        printf("Hello world from thread %d\n", thread_ID);
    }

    end_time = omp_get_wtime();    // 获取结束时间
    time_taken = end_time - start_time;  // 计算时间差

    printf("Time taken: %f seconds\n", time_taken);

    return 0;
}
