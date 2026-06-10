import pandas as pd
import os
import glob

# 设置文件夹路径
folder_path = 'F:/桌面/Deepseek-based_elementextraction-main/GPTbased_elementextraction-main/output'

# 获取所有CSV文件
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
print(f"找到 {len(csv_files)} 个CSV文件")

# 预定义元素列表
elements = ['NULL', 'Mg', 'Al', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Hf', 'Ta', 'W', 'Ir', 'Pt', 'Au', 'Sn', 'Ce']
elements_count = {element: 0 for element in elements}

# 统计满足条件的文献数量
qualified_count = 0
total_count = 0

# 处理所有CSV文件
for csv_file in csv_files:
    print(f"处理文件: {os.path.basename(csv_file)}")

    try:
        # 读取CSV文件
        df_output = pd.read_csv(csv_file)
        file_count = len(df_output)
        total_count += file_count
        print(f"  文件包含 {file_count} 条记录")

        # 处理每一行数据
        for index, row in df_output.iterrows():
            output_str = str(row['output'])

            # 检查是否同时满足三个条件
            conditions_met = (
                    "Article research on Catalytic: Yes" in output_str and
                    "Article research on High entropy materials: Yes" in output_str and
                    "Article Type: Research" in output_str
            )

            if conditions_met:
                qualified_count += 1

                # 提取元素
                if "Specific Elements:" in output_str:
                    # 提取元素部分
                    elements_part = output_str.split("Specific Elements:")[1].strip()
                    # 分割元素并清理
                    element_list = [elem.strip() for elem in elements_part.split(",") if elem.strip()]

                    # 统计元素出现次数
                    for element in element_list:
                        if element in elements_count:
                            elements_count[element] += 1
                        else:
                            # 如果遇到不在预定义列表中的元素，也统计但不加入总数
                            print(f"发现未预定义元素: {element}")
                else:
                    elements_count['NULL'] += 1

    except Exception as e:
        print(f"处理文件 {csv_file} 时出错: {e}")

# 打印统计摘要
print(f"\n统计摘要:")
print(f"总文献数量: {total_count}")
print(f"满足条件的文献数量: {qualified_count}")
print(f"满足条件的文献占比: {qualified_count / total_count * 100:.2f}%" if total_count > 0 else "0%")

# 打印元素统计结果
print(f"\n元素出现次数统计 (仅统计满足条件的文献):")
for element, count in sorted(elements_count.items(), key=lambda x: x[1], reverse=True):
    if count > 0:  # 只显示出现过的元素
        print(f"{element}: {count}")

# 将统计结果写入CSV文件
df = pd.DataFrame(elements_count.items(), columns=['元素', '出现次数'])
df = df.sort_values('出现次数', ascending=False)  # 按出现次数降序排列
output_file = './高熵合金元素组分统计-有条件筛选.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n统计结果已保存到: {output_file}")