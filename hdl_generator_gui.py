import tkinter as tk
from tkinter import scrolledtext

# Funzioni per generare i componenti Verilog (come descritto prima)
def generate_alu():
    alu_code = """
// ALU a 32 bit
module alu (
    input [31:0] A, 
    input [31:0] B, 
    input [3:0] opcode,  // 4 bit per l'operazione (0001 -> Add, 0010 -> Sub, 0011 -> Mul, 0100 -> Div)
    output reg [31:0] result,
    output reg zero_flag
);
    always @(*) begin
        case (opcode)
            4'b0001: result = A + B;      // Addizione
            4'b0010: result = A - B;      // Sottrazione
            4'b0011: result = A * B;      // Moltiplicazione
            4'b0100: result = A / B;      // Divisione
            default: result = 32'b0;      // Default a 0
        endcase
        zero_flag = (result == 32'b0);  // Imposta zero_flag se il risultato è 0
    end
endmodule
"""
    return alu_code

def generate_ram():
    ram_code = """
// Memoria RAM a 256 celle, ognuna lunga 32 bit
module ram (
    input clk,
    input reset,
    input [7:0] address,  // Indirizzo della cella (256 celle = 8 bit)
    input [31:0] data_in,
    input write_enable,
    output reg [31:0] data_out
);
    reg [31:0] memory [255:0];  // Memoria RAM con 256 celle

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            data_out <= 32'b0;  // Resetta l'output
        end else if (write_enable) begin
            memory[address] <= data_in;  // Scrittura nella memoria
        end else begin
            data_out <= memory[address];  // Lettura dalla memoria
        end
    end
endmodule
"""
    return ram_code

def generate_register():
    register_code = """
// Registro a 32 bit
module register (
    input clk,
    input reset,
    input [31:0] data_in,
    input write_enable,
    output reg [31:0] data_out
);
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            data_out <= 32'b0;  // Reset a zero
        end else if (write_enable) begin
            data_out <= data_in;  // Scrittura nel registro
        end
    end
endmodule
"""
    return register_code

def generate_control_unit():
    control_unit_code = """
// Unità di controllo del sistema
module control_unit (
    input clk,
    input reset,
    input [3:0] opcode,
    output reg alu_enable,
    output reg ram_enable,
    output reg register_enable
);
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            alu_enable <= 0;
            ram_enable <= 0;
            register_enable <= 0;
        end else begin
            case (opcode)
                4'b0001: begin  // Operazione ALU (addizione)
                    alu_enable <= 1;
                    ram_enable <= 0;
                    register_enable <= 1;
                end
                4'b0010: begin  // Operazione RAM (scrittura/lettura)
                    alu_enable <= 0;
                    ram_enable <= 1;
                    register_enable <= 0;
                end
                default: begin
                    alu_enable <= 0;
                    ram_enable <= 0;
                    register_enable <= 0;
                end
            endcase
        end
    end
endmodule
"""
    return control_unit_code

def generate_hdl(description):
    """
    Funzione che genera il codice Verilog in base alla descrizione dell'utente.
    """
    hdl_code = ""

    # Cerca e genera codice per ciascun componente in base alla descrizione
    if "ALU" in description:
        hdl_code += generate_alu()
    if "RAM" in description:
        hdl_code += generate_ram()
    if "registro" in description:
        hdl_code += generate_register()
    if "unità di controllo" in description:
        hdl_code += generate_control_unit()

    return hdl_code

# Funzione che gestisce l'evento del bottone per generare il codice Verilog
def on_generate():
    description = description_entry.get("1.0", "end-1c")  # Ottieni la descrizione inserita dall'utente
    if description:
        generated_code = generate_hdl(description)  # Genera il codice Verilog
        result_text.delete(1.0, tk.END)  # Pulisce l'area di testo precedente
        result_text.insert(tk.END, generated_code)  # Mostra il codice generato
    else:
        result_text.delete(1.0, tk.END)  # Pulisce l'area di testo
        result_text.insert(tk.END, "Inserisci una descrizione valida.")

# Crea la finestra principale
root = tk.Tk()
root.title("Generatore di Codice Verilog")

# Etichetta per la descrizione
description_label = tk.Label(root, text="Inserisci la descrizione del sistema:")
description_label.pack(pady=10)

# Area di testo per la descrizione dell'utente
description_entry = scrolledtext.ScrolledText(root, width=50, height=10)
description_entry.pack(pady=10)

# Bottone per generare il codice Verilog
generate_button = tk.Button(root, text="Genera Codice Verilog", command=on_generate)
generate_button.pack(pady=10)

# Area di testo per visualizzare il codice Verilog generato
result_text = scrolledtext.ScrolledText(root, width=80, height=20)
result_text.pack(pady=10)

# Avvia la GUI
root.mainloop()