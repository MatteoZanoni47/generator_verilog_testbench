import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def parse_verilog(file_path):
    """
    Analizza il file Verilog per estrarre:
    - Nome del modulo
    - Porte con tipo (input, output, inout)
    - Larghezze di bus
    """
    with open(file_path, 'r') as file:
        code = file.read()

    # Trova il nome del modulo
    module_match = re.search(r'\bmodule\s+(\w+)', code)
    if not module_match:
        raise ValueError("Modulo non trovato nel file Verilog.")
    module_name = module_match.group(1)

    # Trova le dichiarazioni delle porte
    ports_match = re.findall(r'(input|output|inout)\s+((\[[^\]]+\])?\s*\w+)', code)
    if not ports_match:
        raise ValueError("Nessuna porta trovata nel modulo.")
    
    # Estrarre le porte
    ports = []
    for port in ports_match:
        port_type = port[0]
        port_width = port[2].strip() if port[2] else ''  # Larghezza del bus
        port_name = re.search(r'\w+$', port[1]).group(0)
        ports.append({
            'type': port_type,
            'width': port_width,
            'name': port_name
        })
    
    return module_name, ports


def generate_uvm_testbench(module_name, ports):
    """
    Genera un testbench UVM completo con driver, monitor e sequenze.
    """
    tb_code = []
    
    # Header
    tb_code.append("`timescale 1ns/1ps")
    tb_code.append(f"module {module_name}_tb;\n")

    # Dichiarazione dei segnali
    tb_code.append("    // Dichiarazione dei segnali")
    for port in ports:
        if port['type'] == 'input':
            tb_code.append(f"    reg {port['width']} {port['name']};")
        elif port['type'] == 'output':
            tb_code.append(f"    wire {port['width']} {port['name']};")
        elif port['type'] == 'inout':
            tb_code.append(f"    wire {port['width']} {port['name']};")
    tb_code.append("")

    # Instanziazione del modulo
    tb_code.append("    // Instanziazione del modulo DUT")
    tb_code.append(f"    {module_name} uut (")
    for port in ports:
        tb_code.append(f"        .{port['name']}({port['name']}),")
    tb_code[-1] = tb_code[-1][:-1]  # Rimuove l'ultima virgola
    tb_code.append("    );\n")

    # Clock e Reset automatici
    clk_signal = next((p['name'] for p in ports if p['name'].lower().startswith('clk')), None)
    rst_signal = next((p['name'] for p in ports if p['name'].lower().startswith('rst')), None)
    if clk_signal:
        tb_code.append(f"    // Generazione del clock")
        tb_code.append(f"    always #5 {clk_signal} = ~{clk_signal};")
    tb_code.append("")
    if rst_signal:
        tb_code.append(f"    // Gestione del reset")
        tb_code.append(f"    initial begin")
        tb_code.append(f"        {rst_signal} = 1;")
        tb_code.append(f"        #10 {rst_signal} = 0;")
        tb_code.append(f"    end\n")

    # Ambiente UVM
    tb_code.append("    // Istanziazione del testbench UVM")
    tb_code.append("    initial begin")
    tb_code.append("        uvm_config_db#(virtual interface).set(this, \"\", \"vif\", vif);")
    tb_code.append("        run_test();")
    tb_code.append("    end\n")

    tb_code.append("endmodule\n")
    return "\n".join(tb_code)


def generate_uvm_environment(module_name, ports, output_dir):
    """
    Genera i file UVM per driver, monitor, e sequenze.
    """
    env_files = {}
    
    # Interface
    vif_code = []
    vif_code.append(f"interface {module_name}_if;")
    for port in ports:
        vif_code.append(f"    logic {port['width']} {port['name']};")
    vif_code.append("endinterface\n")
    env_files[f"{module_name}_if.sv"] = "\n".join(vif_code)

    # Driver
    driver_code = []
    driver_code.append(f"class {module_name}_driver extends uvm_driver;")
    driver_code.append("    // Implementa il driver")
    driver_code.append("endclass\n")
    env_files[f"{module_name}_driver.sv"] = "\n".join(driver_code)

    # Monitor
    monitor_code = []
    monitor_code.append(f"class {module_name}_monitor extends uvm_monitor;")
    monitor_code.append("    // Implementa il monitor")
    monitor_code.append("endclass\n")
    env_files[f"{module_name}_monitor.sv"] = "\n".join(monitor_code)

    # Sequence
    sequence_code = []
    sequence_code.append(f"class {module_name}_sequence extends uvm_sequence;")
    sequence_code.append("    // Implementa la sequenza")
    sequence_code.append("endclass\n")
    env_files[f"{module_name}_sequence.sv"] = "\n".join(sequence_code)

    # Scrivi i file nell'output_dir
    for file_name, file_content in env_files.items():
        with open(os.path.join(output_dir, file_name), 'w') as f:
            f.write(file_content)


def open_file():
    """Apre un file di Verilog."""
    file_path = filedialog.askopenfilename(filetypes=[("Verilog Files", "*.v")])
    return file_path


def generate_files():
    """Gestisce la generazione di testbench e UVM da GUI."""
    file_path = open_file()
    if not file_path:
        return

    output_dir = filedialog.askdirectory()
    if not output_dir:
        return

    try:
        # Parsing e generazione
        module_name, ports = parse_verilog(file_path)
        
        # Genera Testbench
        tb_code = generate_uvm_testbench(module_name, ports)
        tb_file = os.path.join(output_dir, f"{module_name}_tb.sv")
        with open(tb_file, 'w') as f:
            f.write(tb_code)

        # Genera Ambiente UVM
        generate_uvm_environment(module_name, ports, output_dir)

        messagebox.showinfo("Successo", f"Testbench UVM generato in {output_dir}")
    except Exception as e:
        messagebox.showerror("Errore", str(e))


# GUI con Tkinter
def create_gui():
    root = tk.Tk()
    root.title("Generatore di Testbench UVM")

    tk.Label(root, text="Generatore di Testbench UVM", font=("Arial", 16)).pack(pady=10)

    tk.Button(root, text="Seleziona file Verilog e genera", command=generate_files).pack(pady=20)

    root.geometry("400x200")
    root.mainloop()


if __name__ == "__main__":
    create_gui()
