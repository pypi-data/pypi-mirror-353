#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import threading
import pymysql
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any, Union, Optional, Callable, Tuple

class DataSyncUtils:
    """数据同步工具类，提供高效的数据库操作方法"""
    
    @staticmethod
    def default_batch_callback(batch_id: int, count: int, elapsed: float) -> None:
        """
        默认的批处理回调函数，输出批处理结果统计
        
        参数:
            batch_id: 批次ID
            count: 处理的记录数
            elapsed: 处理耗时(秒)
        """
        speed = count / elapsed if elapsed > 0 else 0
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 子批次 {batch_id} 完成: {count} 条记录, "
              f"耗时 {elapsed:.2f} 秒, 速率: {speed:.1f} 条/秒")
    
    @staticmethod
    def batch_insert_worker(
        batch_data: List[List[Any]], 
        insert_sql: str, 
        db_config: Dict[str, Any], 
        batch_id: int,
        callback: Optional[Callable] = None
    ) -> int:
        """
        并行批量插入工作线程
        
        参数:
            batch_data: 要插入的数据批次
            insert_sql: 预编译的插入SQL语句
            db_config: 数据库连接配置
            batch_id: 批次ID，用于日志
            callback: 可选的回调函数，处理每批次结果后调用
            
        返回:
            插入的记录数
        """
        conn = None
        cursor = None
        start_time = time.time()
        try:
            # 创建新连接而不是从连接池获取，避免并发问题
            conn = pymysql.connect(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"],
                charset=db_config["charset"],
                connect_timeout=db_config.get("connect_timeout", 10),
                read_timeout=db_config.get("read_timeout", 30),
                write_timeout=db_config.get("write_timeout", 30),
                local_infile=db_config.get("local_infile", 1),
                autocommit=False,  # 禁用自动提交
                max_allowed_packet=db_config.get("max_allowed_packet", 16*1024*1024)
            )
            cursor = conn.cursor()
            
            # 设置会话变量以优化批量插入
            cursor.execute("SET SESSION tidb_distsql_scan_concurrency=15")  # 调整扫描并发
            cursor.execute("SET SESSION tidb_dml_batch_size=128")  # 批处理大小
            
            # 执行批量插入
            cursor.executemany(insert_sql, batch_data)
            conn.commit()
            
            elapsed = time.time() - start_time
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 批次 {batch_id} 完成: 插入 {len(batch_data)} 条记录, 耗时 {elapsed:.2f} 秒")
            
            # 如果有回调函数，则调用
            if callback:
                callback(batch_id, len(batch_data), elapsed)
                
            return len(batch_data)
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 批次 {batch_id} 失败: {str(e)}")
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def parallel_write_to_db(
        data: Union[pd.DataFrame, List[Dict[str, Any]]],
        db_config: Dict[str, Any],
        columns: List[str] = None,
        batch_size: int = 2000,
        max_workers: int = 20,
        insert_method: str = "update",
        primary_keys: List[str] = None,
        callback: Optional[Callable] = None,
        encrypted_columns: List[str] = None,
        encryption_key: str = "petlibro123"
    ) -> Tuple[int, float, List[str]]:
        """
        并行写入数据到数据库
        
        参数:
            data: 要写入的数据，可以是Pandas DataFrame或字典列表
            db_config: 数据库连接配置，必须包含host, port, user, password, database, table等字段
            columns: 列名列表，如果为None则从data中推断
            batch_size: 每批次处理的记录数
            max_workers: 并行工作线程的最大数量
            insert_method: 插入方法，可选值为'update'(更新),'ignore'(忽略重复),'direct'(直接插入)
            primary_keys: 主键列表，用于构建ON DUPLICATE KEY UPDATE语句，仅在insert_method='update'时有效
            callback: 可选的回调函数，处理每批次结果后调用，如果未提供则使用默认回调函数
            encrypted_columns: 需要加密的列名列表，这些列将使用TiDB的AES_ENCRYPT函数加密
            encryption_key: 加密密钥，默认为'petlibro123'
            
        返回:
            (插入记录数, 总耗时, 警告信息列表)
        """
        start_time = time.time()
        warnings = []
        
        # 如果未提供回调函数，使用默认回调
        if callback is None:
            callback = DataSyncUtils.default_batch_callback
        
        # 处理输入数据
        if isinstance(data, pd.DataFrame):
            # 如果是DataFrame，转换为字典列表
            if columns is None:
                columns = data.columns.tolist()
            
            # 处理NaN和None值
            for col in data.columns:
                data[col] = data[col].replace({pd.NA: None, float('nan'): None})
            
            # 转换为记录列表
            rows = []
            for _, row in data.iterrows():
                # 按列顺序提取值
                values = [row.get(col, None) for col in columns]
                rows.append(values)
        else:
            # 如果是字典列表
            if columns is None and data:
                # 从第一条记录推断列
                columns = list(data[0].keys())
            
            # 转换为记录列表
            rows = []
            for row in data:
                # 按列顺序提取值
                values = [row.get(col, None) for col in columns]
                rows.append(values)
        
        total_rows = len(rows)
        if total_rows == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 没有数据需要写入")
            return 0, 0, warnings
        
        # 构建SQL语句
        table_name = db_config["table"]
        
        # 如果有加密列，需要特殊处理SQL构建
        if encrypted_columns:
            encrypted_columns_set = set(encrypted_columns)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检测到加密列: {encrypted_columns}")
            
            # 构建列名和值的部分
            column_parts = []
            value_parts = []
            
            for col in columns:
                column_parts.append(f"`{col}`")
                if col in encrypted_columns_set:
                    # 对加密字段使用AES加密和Base64编码
                    value_parts.append(f"TO_BASE64(AES_ENCRYPT(%s, '{encryption_key}'))")
                else:
                    value_parts.append("%s")
            
            column_names = ', '.join(column_parts)
            placeholders = ', '.join(value_parts)
        else:
            # 普通模式，不加密
            column_names = ', '.join(['`' + col + '`' for col in columns])
            placeholders = ', '.join(['%s'] * len(columns))
        
        if insert_method == 'update':
            # 更新模式: INSERT ... ON DUPLICATE KEY UPDATE
            if not primary_keys:
                # 如果没有提供主键，假设第一列是主键
                primary_keys = [columns[0]]
            
            # 构建更新部分，排除主键字段
            update_columns = [col for col in columns if col not in primary_keys]
            
            if encrypted_columns:
                encrypted_columns_set = set(encrypted_columns)
                update_parts = []
                for col in update_columns:
                    if col in encrypted_columns_set:
                        # 对加密字段使用AES加密
                        update_parts.append(f"`{col}` = TO_BASE64(AES_ENCRYPT(VALUES(`{col}`), '{encryption_key}'))")
                    else:
                        update_parts.append(f"`{col}` = VALUES(`{col}`)")
                update_stmt = ', '.join(update_parts)
            else:
                update_stmt = ', '.join([f"`{col}` = VALUES(`{col}`)" for col in update_columns])
            
            insert_sql = f"""
                INSERT /*+ SET_VAR(tidb_dml_type='bulk') */ INTO {table_name} ({column_names})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {update_stmt};
            """
        elif insert_method == 'ignore':
            # 忽略模式: INSERT IGNORE INTO
            insert_sql = f"""
                INSERT /*+ SET_VAR(tidb_dml_type='bulk') */ IGNORE INTO {table_name} ({column_names})
                VALUES ({placeholders});
            """
        else:
            # 直接插入模式: INSERT INTO
            insert_sql = f"""
                INSERT /*+ SET_VAR(tidb_dml_type='bulk') */ INTO {table_name} ({column_names})
                VALUES ({placeholders});
            """
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SQL: {insert_sql}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始并行写入数据到{db_config['table']}，总记录数: {total_rows}")
        
        # 分配数据到批次
        batches = []
        for i in range(0, total_rows, batch_size):
            end = min(i + batch_size, total_rows)
            batch_data = rows[i:end]
            batches.append(batch_data)
        
        # 限制工作线程数量
        actual_workers = min(max_workers, len(batches))
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 使用 {actual_workers} 个工作线程处理 {len(batches)} 个批次")
        
        # 使用ThreadPoolExecutor并行处理批次
        inserted_count = 0
        failed_batches = 0
        
        with ThreadPoolExecutor(max_workers=actual_workers) as executor:
            # 提交所有批次任务
            future_to_batch = {
                executor.submit(
                    DataSyncUtils.batch_insert_worker, 
                    batch, 
                    insert_sql, 
                    db_config, 
                    i,
                    callback
                ): i for i, batch in enumerate(batches)
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_batch):
                batch_id = future_to_batch[future]
                try:
                    data_count = future.result()
                    inserted_count += data_count
                    completion_percentage = inserted_count / total_rows * 100
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 进度: {inserted_count}/{total_rows} 条记录 ({completion_percentage:.1f}%)")
                except Exception as e:
                    failed_batches += 1
                    error_msg = f"批次 {batch_id} 处理失败: {str(e)}"
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}")
                    warnings.append(error_msg)
        
        total_time = time.time() - start_time
        rate = inserted_count / total_time if total_time > 0 else 0
        
        summary = (
            f"数据写入完成，共写入 {inserted_count}/{total_rows} 条记录，"
            f"失败批次: {failed_batches}，"
            f"总耗时: {total_time:.2f} 秒，"
            f"平均速度: {rate:.1f} 条/秒"
        )
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {summary}")
        
        return inserted_count, total_time, warnings
    
    @staticmethod
    def process_single_chunk(chunk_info, db_config, primary_keys, table_name):
        """
        处理单个数据分块的函数
        
        参数:
            chunk_info: 包含chunk_id和chunk_pandas_df的元组
            db_config: 数据库连接配置
            primary_keys: 主键列表
            table_name: 表名
            
        返回:
            处理结果字典，包含成功状态、插入记录数、耗时等信息
        """
        chunk_id, chunk_pandas_df = chunk_info
        thread_id = threading.current_thread().ident
        
        print(f"[Thread-{thread_id}] Processing chunk {chunk_id} with {len(chunk_pandas_df)} records for {table_name}")
        
        try:
            start_time = time.time()
            inserted_count, duration, batch_warnings = DataSyncUtils.parallel_write_to_db(
                data=chunk_pandas_df,
                db_config=db_config,
                batch_size=2000,  # 批次大小
                max_workers=60,   # 减少每个分块的并发数，因为现在是多分块并发
                insert_method='update',
                primary_keys=primary_keys
            )
            
            processing_time = time.time() - start_time
            print(f"[Thread-{thread_id}] Chunk {chunk_id} completed: {inserted_count} records inserted in {processing_time:.2f}s")
            
            return {
                'chunk_id': chunk_id,
                'inserted_count': inserted_count,
                'duration': duration,
                'processing_time': processing_time,
                'warnings': batch_warnings or [],
                'success': True,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Error processing chunk {chunk_id}: {str(e)}"
            print(f"[Thread-{thread_id}] {error_msg}")
            return {
                'chunk_id': chunk_id,
                'inserted_count': 0,
                'duration': 0,
                'processing_time': 0,
                'warnings': [error_msg],
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def process_data_in_chunks(spark_df, chunk_size, db_config, primary_keys, table_name, max_concurrent_chunks=4):
        """
        并发分块处理大数据集并写入数据库
        
        参数:
            spark_df: Spark DataFrame数据源
            chunk_size: 每个分块的记录数
            db_config: 数据库连接配置
            primary_keys: 主键列表
            table_name: 表名
            max_concurrent_chunks: 最大并发分块数，默认为4
            
        返回:
            (总插入记录数, 总处理时间, 警告信息列表)
        """
        # 导入Spark相关依赖（如果可用）
        try:
            from pyspark.sql.window import Window
            from pyspark.sql.functions import row_number
        except ImportError:
            raise ImportError("此功能需要安装PySpark。请运行：pip install pyspark")
        
        total_count = spark_df.count()
        print(f"Total records in {table_name}: {total_count}")
        
        if total_count == 0:
            print(f"No data to process for {table_name}")
            return 0, 0, []
        
        # 计算需要多少个分块
        num_chunks = (total_count + chunk_size - 1) // chunk_size
        print(f"Processing {table_name} in {num_chunks} chunks of {chunk_size} records each")
        print(f"Using {max_concurrent_chunks} concurrent chunk processors")
        
        # 添加行号用于分块
        window = Window.orderBy("ts", "device_sn")  # 按时间戳和设备SN排序
        spark_df_with_rn = spark_df.withColumn("row_number", row_number().over(window))
        
        # 缓存以提高后续操作性能
        spark_df_with_rn.cache()
        
        # 预处理所有分块，转换为Pandas DataFrame
        print("Preparing chunks for concurrent processing...")
        chunk_data_list = []
        
        for i in range(num_chunks):
            start_idx = i * chunk_size + 1
            end_idx = min((i + 1) * chunk_size, total_count)
            
            print(f"Preparing chunk {i+1}/{num_chunks} (records {start_idx} to {end_idx})")
            
            # 使用行号来获取分块数据
            chunk_df = spark_df_with_rn.filter(
                (spark_df_with_rn.row_number >= start_idx) & 
                (spark_df_with_rn.row_number <= end_idx)
            ).drop("row_number")
            
            chunk_pandas_df = chunk_df.toPandas()
            
            if len(chunk_pandas_df) > 0:
                chunk_data_list.append((i+1, chunk_pandas_df))
        
        # 清理缓存
        spark_df_with_rn.unpersist()
        
        if not chunk_data_list:
            print(f"No valid chunks to process for {table_name}")
            return 0, 0, []
        
        print(f"Starting concurrent processing of {len(chunk_data_list)} chunks...")
        
        total_inserted = 0
        total_duration = 0
        all_warnings = []
        successful_chunks = 0
        failed_chunks = 0
        
        # 使用ThreadPoolExecutor进行并发处理
        with ThreadPoolExecutor(max_workers=max_concurrent_chunks) as executor:
            # 提交所有任务
            future_to_chunk = {
                executor.submit(DataSyncUtils.process_single_chunk, chunk_info, db_config, primary_keys, table_name): chunk_info[0]
                for chunk_info in chunk_data_list
            }
            
            # 收集结果
            for future in as_completed(future_to_chunk):
                chunk_id = future_to_chunk[future]
                try:
                    result = future.result()
                    
                    if result['success']:
                        total_inserted += result['inserted_count']
                        total_duration += result['duration']
                        successful_chunks += 1
                    else:
                        failed_chunks += 1
                    
                    if result['warnings']:
                        all_warnings.extend(result['warnings'])
                        
                except Exception as e:
                    error_msg = f"Exception occurred while processing chunk {chunk_id}: {str(e)}"
                    print(error_msg)
                    all_warnings.append(error_msg)
                    failed_chunks += 1
        
        print("="*50)
        print(f"Concurrent processing completed for {table_name}:")
        print(f"  - Successful chunks: {successful_chunks}")
        print(f"  - Failed chunks: {failed_chunks}")
        print(f"  - Total records inserted: {total_inserted}")
        print(f"  - Total processing time: {total_duration:.2f}s")
        print("="*50)
        
        return total_inserted, total_duration, all_warnings 