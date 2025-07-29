import os

# Sử dụng import tương đối
from .kmap import (
    parse_groups,
    generate_kmap,
    kmap_to_latex,
    get_cell_positions,
    generate_tikz_code, # Đây là hàm đã được giữ lại và dọn dẹp
    kmap_to_tikz_latex,
    generate_latex as generate_kmap_solution_latex, # Đổi tên để rõ nghĩa hơn với vai trò của nó
    create_full_latex_document as create_kmap_latex_document
)

def run_kmap_tests():
    print("--- Testing lo_gateimg_tool.kmap module ---")

    # --- Test Data ---
    # 3-variable example
    vars_3 = "a,b,c"
    minterms_3 = "1,2,5,6"
    dontcares_3 = "0"
    groups_str_3 = "GROUP1 (1,5)\\nGROUP2 (2,0)" # Group 2 includes a don't care
    result_expr_3 = "f(a,b,c) = c'b + ab'" # Ví dụ kết quả mong đợi

    # 4-variable example
    vars_4 = "w,x,y,z"
    minterms_4 = "0,1,2,3,4,6,8,9,10,12"
    dontcares_4 = "14,15"
    groups_str_4 = "GROUP1 (0,1,2,3)\\nGROUP2 (0,4,8,12)\\nGROUP3 (2,6,10,14)" # Group 3 includes a don't care
    result_expr_4 = "f(w,x,y,z) = w'y' + x'z' + w'x'" # Ví dụ kết quả mong đợi

    print("\\n--- Testing with 3-variable K-map ---")
    print(f"Variables: {vars_3}")
    print(f"Minterms: {minterms_3}")
    print(f"Don't Cares: {dontcares_3}")
    print(f"Groups String: \\n{groups_str_3}")

    parsed_groups_3 = parse_groups(groups_str_3)
    print(f"Parsed Groups (3-var): {parsed_groups_3}")
    assert parsed_groups_3 == ['1,5', '2,0'], f"Test Failed: parse_groups_3 - Expected ['1,5', '2,0'], Got {parsed_groups_3}"

    kmap_3, mapping_3 = generate_kmap(vars_3, minterms_3, dontcares_3)
    print("Generated K-map (3-var):")
    for row in kmap_3:
        print(row)
    # Thêm một vài assert cơ bản
    assert kmap_3[0][1] == 1, "Test Failed: kmap_3[0][1] for minterm 1"
    assert kmap_3[0][0] == 'x', "Test Failed: kmap_3[0][0] for dontcare 0"
    
    print(f"Mapping (3-var): {mapping_3}")

    latex_kmap_3 = kmap_to_latex(kmap_3, is_4var=False)
    print(f"LaTeX K-map (3-var):\\n{latex_kmap_3}")
    assert "a \\\\backslash bc" in latex_kmap_3, "Test Failed: LaTeX 3-var table header"

    if parsed_groups_3:
        group_1_cells_3 = get_cell_positions(parsed_groups_3[0], mapping_3)
        print(f"Cell positions for group '{parsed_groups_3[0]}': {group_1_cells_3}")
        assert group_1_cells_3 == [(0,1), (1,1)], f"Test Failed: Cell positions for group 1,5 - Got {group_1_cells_3}"
        
        all_group_cells_3 = [get_cell_positions(g, mapping_3) for g in parsed_groups_3]
        
        if all_group_cells_3 and any(all_group_cells_3):
            tikz_code_3 = generate_tikz_code(kmap_3, all_group_cells_3, is_4var=False)
            print(f"TikZ Code for K-map groups (3-var):\\n{tikz_code_3}")
            assert "\\draw[red" in tikz_code_3, "Test Failed: TikZ code should contain drawing commands for 3-var"

            tikz_via_kmap_to_tikz_3 = kmap_to_tikz_latex(kmap_3, parsed_groups_3, mapping_3, is_4var=False)
            print(f"TikZ via kmap_to_tikz_latex (3-var):\\n{tikz_via_kmap_to_tikz_3}")
            assert tikz_via_kmap_to_tikz_3 == tikz_code_3, "Test Failed: kmap_to_tikz_latex should match generate_tikz_code for 3-var"
        else:
            print("Skipping TikZ generation for 3-var due to empty/invalid group cell positions.")

    print("\\n--- Testing with 4-variable K-map ---")
    # (Tương tự cho 4 biến, có thể thêm các assert cụ thể)
    parsed_groups_4 = parse_groups(groups_str_4)
    print(f"Parsed Groups (4-var): {parsed_groups_4}")

    kmap_4, mapping_4 = generate_kmap(vars_4, minterms_4, dontcares_4)
    print("Generated K-map (4-var):")
    latex_kmap_4 = kmap_to_latex(kmap_4, is_4var=True)
    print(f"LaTeX K-map (4-var):\\n{latex_kmap_4}")
    assert "ab \\\\backslash cd" in latex_kmap_4, "Test Failed: LaTeX 4-var table header"

    if parsed_groups_4 and any(get_cell_positions(g, mapping_4) for g in parsed_groups_4):
        all_group_cells_4 = [get_cell_positions(g, mapping_4) for g in parsed_groups_4]
        tikz_code_4 = generate_tikz_code(kmap_4, all_group_cells_4, is_4var=True)
        print(f"TikZ Code for K-map groups (4-var):\\n{tikz_code_4}")
        assert "\\draw[red" in tikz_code_4, "Test Failed: TikZ code should contain drawing commands for 4-var"
    else:
        print("Skipping TikZ generation for 4-var due to empty/invalid group cell positions or no groups.")

    print("\\n--- Testing generate_kmap_solution_latex and create_kmap_latex_document ---")
    mock_row_data_3_var = {
        "Case": "Test_Kmap_3_Var",
        "Function": f"f({vars_3}) = {minterms_3} + dontcares: {dontcares_3}",
        "Result": result_expr_3,
        "Groups": groups_str_3
    }
    
    data_input_3, data_solution_3, data_output_3 = generate_kmap_solution_latex(mock_row_data_3_var)
    if data_input_3:
        print(f"Generated data_input for K-map solution (3-var):\\n{data_input_3[:100]}...")
        print(f"Generated data_solution for K-map (3-var):\\n{data_solution_3[:200]}...")
        print(f"Generated data_output for K-map (3-var): {data_output_3}")
        assert result_expr_3 in data_output_3, "Test Failed: Kmap solution output string mismatch"

        full_doc_3 = create_kmap_latex_document(data_input_3, data_solution_3, mock_row_data_3_var["Case"])
        print(f"Full K-map LaTeX Document (3-var) starts with:\\n{full_doc_3[:200]}...")
        assert "\\documentclass{article}" in full_doc_3, "Test Failed: Full Kmap LaTeX doc preamble"
        assert mock_row_data_3_var["Case"] in full_doc_3, "Test Failed: Case number in full Kmap LaTeX doc"
    else:
        print("generate_kmap_solution_latex returned None for 3-var mock data.")
        
    print("\\n--- End of lo_gateimg_tool.kmap module tests ---")

if __name__ == "__main__":
    # Để chạy script này trực tiếp từ dòng lệnh:
    # 1. Đảm bảo bạn đang ở thư mục `digi_solver` (thư mục cha của `lo_gateimg_tool`).
    # 2. Chạy lệnh: python -m lo_gateimg_tool.test_kmap_module
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(current_script_dir, "__init__.py")):
        print("CẢNH BÁO: Không tìm thấy file __init__.py trong thư mục chứa script này.")
    run_kmap_tests() 