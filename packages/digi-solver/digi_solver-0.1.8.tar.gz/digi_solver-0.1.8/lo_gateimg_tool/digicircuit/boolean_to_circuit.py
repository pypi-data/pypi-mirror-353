import os
# import argparse # Không cần thiết nữa
from .boolean_parser import create_circuits_from_expressions # Thay đổi import
from .latex_export import LatexExporter

def generate_circuits_from_file_content(input_file_path: str, output_dir: str, scale: float = 1.0):
    """ 
    Reads Boolean expressions from an input file, generates LaTeX circuit diagrams,
    and saves them to the specified output directory.

    Args:
        input_file_path: Path to the input file containing Boolean expressions.
        output_dir: Directory to save the generated .tex files.
        scale: Scale factor for the circuit diagrams.

    Returns:
        A list of paths to the generated .tex files.
    """
    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found")
        return []
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(input_file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    functions_str_list = []
    for line in lines:
        parts = line.split(' ', 1)
        if len(parts) > 1 and parts[0].isdigit():
            functions_str_list.append(parts[1])
        else:
            functions_str_list.append(line)

    if not functions_str_list:
        print("No functions found in the input file.")
        return []

    print(f"Functions to process: {functions_str_list}")

    # Sử dụng hàm mới từ boolean_parser, không cần file tạm nữa
    circuits = create_circuits_from_expressions(functions_str_list)

    if not circuits:
        print("Could not create any circuits from the provided functions.")
        return []

    seen_functions = set()
    unique_circuits_data = []
    # zip circuits với functions_str_list gốc để giữ đúng thứ tự và nội dung cho việc loại bỏ trùng lặp
    # và đặt tên file
    for circuit, func_str in zip(circuits, functions_str_list):
        # Kiểm tra xem func_str có hợp lệ để thêm vào seen_functions không
        # (ví dụ, nếu create_circuits_from_expressions trả về ít circuit hơn functions_str_list do lỗi parse)
        # Tuy nhiên, create_circuits_from_expressions hiện đang tạo một circuit (có thể rỗng) cho mỗi func_str
        if func_str not in seen_functions:
            seen_functions.add(func_str)
            unique_circuits_data.append((circuit, func_str))

    generated_files = []
    for i, (circuit, func_str) in enumerate(unique_circuits_data, 1):
        exporter = LatexExporter(circuit) # Giả sử LatexExporter có thể nhận circuit object
        # Cần kiểm tra lại LatexExporter(__init__) nếu nó mong đợi dict thay vì object
        
        safe_func_name_part = func_str.split('=')[0].strip().replace('(','_').replace(')','').replace(',','').replace(' ','')
        # Loại bỏ các ký tự không hợp lệ cho tên file kỹ hơn
        safe_func_name_part = "".join(c if c.isalnum() or c in ('_', '-') else '' for c in safe_func_name_part)
        if not safe_func_name_part: # Nếu tên rỗng sau khi làm sạch
            safe_func_name_part = f"func{i}"
        else:
            safe_func_name_part = f"{safe_func_name_part}_{i}"

        output_filename = f"circuit_{safe_func_name_part}.tex"
        
        full_output_path = os.path.join(output_dir, output_filename)
        exporter.save_to_file(output_dir, output_filename, scale=scale, function_str=func_str)
        print(f"Generated {full_output_path}")
        generated_files.append(full_output_path)
    
    return generated_files

# Bỏ phần if __name__ == "__main__": và parser vì sẽ không chạy trực tiếp nữa
# def main():
#     parser = argparse.ArgumentParser(description='Convert Boolean expressions to circuit diagrams.')
#     parser.add_argument('input_file', help='Input file with Boolean expressions')
#     ...
#     args = parser.parse_args()
#     ...
#     # Gọi hàm mới ở đây nếu cần test từ CLI, nhưng mục tiêu là gọi từ code khác
#     generate_circuits_from_file_content(args.input_file, args.output_dir, args.scale)

# if __name__ == "__main__":
# exit(main()) 