import random
import os

TEXT_1 = """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_unsigned.all;

entity project_tb is
end project_tb;

architecture projecttb of project_tb is
constant c_CLOCK_PERIOD         : time := 15 ns;
signal   tb_done                : std_logic;
signal   mem_address            : std_logic_vector (15 downto 0) := (others => '0');
signal   tb_rst                 : std_logic := '0';
signal   tb_start               : std_logic := '0';
signal   tb_clk                 : std_logic := '0';
signal   mem_o_data,mem_i_data  : std_logic_vector (7 downto 0);
signal   enable_wire            : std_logic;
signal   mem_we                 : std_logic;
--signal   test_read              : std_logic;
--signal   test_process           : integer;
--signal   test_write             : integer;
--signal   test_address           : std_logic_vector (15 downto 0);
--signal   test_end_address       : std_logic_vector (15 downto 0);

type ram_type is array (65535 downto 0) of std_logic_vector(7 downto 0);
"""

TEXT_2 = """
component project_reti_logiche is
port (
      i_clk         : in  std_logic;
      i_rst         : in  std_logic;
      i_start       : in  std_logic;
      i_data        : in  std_logic_vector(7 downto 0);
      o_address     : out std_logic_vector(15 downto 0);
      o_done        : out std_logic;
      o_en          : out std_logic;
      o_we          : out std_logic;
      o_data        : out std_logic_vector (7 downto 0)
--      t_read        : out std_logic;
--      t_process     : out integer;
--      t_write       : out integer;
--      t_address     : out std_logic_vector(15 downto 0);
--      t_end_addr    : out std_logic_vector(15 downto 0) 
      );
end component project_reti_logiche;


begin
UUT: project_reti_logiche
port map (
          i_clk      	=> tb_clk,
          i_rst      	=> tb_rst,
          i_start       => tb_start,
          i_data    	=> mem_o_data,
          o_address  	=> mem_address,
          o_done      	=> tb_done,
          o_en   	    => enable_wire,
          o_we 		    => mem_we,
          o_data    	=> mem_i_data
 --         t_read        => test_read,
--          t_process     => test_process,
--          t_write       => test_write,
--          t_address     => test_address,
--          t_end_addr    => test_end_address
          );

p_CLK_GEN : process is
begin
    wait for c_CLOCK_PERIOD/2;
    tb_clk <= not tb_clk;
end process p_CLK_GEN;


MEM : process(tb_clk)
begin
    if tb_clk'event and tb_clk = '1' then
        if enable_wire = '1' then
            if mem_we = '1' then
                RAM(conv_integer(mem_address))  <= mem_i_data;
                mem_o_data                      <= mem_i_data after 2 ns;
            else
                mem_o_data <= RAM(conv_integer(mem_address)) after 2 ns;
            end if;
        end if;
    end if;
end process;


test : process is
begin 
    wait for 100 ns;
    wait for c_CLOCK_PERIOD;
    tb_rst <= '1';
    wait for c_CLOCK_PERIOD;
    wait for 100 ns;
    tb_rst <= '0';
    wait for c_CLOCK_PERIOD;
    wait for 100 ns;
    tb_start <= '1';
    wait for c_CLOCK_PERIOD;
    wait until tb_done = '1';
    wait for c_CLOCK_PERIOD;
    tb_start <= '0';
    wait until tb_done = '0';
    wait for 100 ns;
"""

TEXT_3 = """
    assert false report "Simulation Ended! TEST PASSATO" severity failure;
end process test;

end projecttb; 
"""


MAX_NUM = 255
MAX_LEN = 255
MIN_LEN = 0


def get_size():
    return random.randint(MIN_LEN, min(MAX_LEN, MAX_NUM))


def generate_input(size):
    res = []
    for i in range(size):
        res.append(random.randint(0, MAX_NUM))
    return res


FSA = {
    "00": {"out": ["00", "11"], "next": ["00", "10"]},
    "01": {"out": ["11", "00"], "next": ["00", "10"]},
    "10": {"out": ["01", "10"], "next": ["01", "11"]},
    "11": {"out": ["10", "01"], "next": ["01", "11"]},
}


def u_to_y(u, starting):
    state = starting
    out_string = ""
    in_string = format(u + 256, 'b')[1:]
    for b in in_string:
        out_string += FSA[state]["out"][int(b)]
        state = FSA[state]["next"][int(b)]
    return [int(out_string[:8], 2), int(out_string[8:], 2)], state


def calculate_output(in_list):
    out_list = []
    starting_state = "00"
    for i in in_list:
        new_list, starting_state = u_to_y(i, starting_state)
        out_list += new_list
    return out_list


def generate_text(in_list, out_list):
    full_text = TEXT_1

    # add input dependent lines
    full_text += "\nsignal RAM: ram_type := ("
    for i, n in enumerate([len(in_list)] + in_list):
        full_text += str(i) + " => std_logic_vector(to_unsigned(  " + str(n) + "  , 8)),\n"
    full_text += "others => (others =>'0'));\n"

    full_text += TEXT_2

    # add comments lines
    full_text += "\n\t-- Input= " + str(in_list)
    full_text += "\n\t-- Output= " + str(out_list) + "\n\n"

    # add output dependent lines
    for i, n in enumerate(out_list):
        full_text += '\tassert RAM(' + str(1000 + i)
        full_text += ') = std_logic_vector(to_unsigned( ' + str(n)
        full_text += ' , 8)) report "TEST FALLITO (WORKING ZONE). Expected  ' + str(n)
        full_text += '  found " & integer\'image(to_integer(unsigned(RAM(' + str(1000 + i)
        full_text += '))))  severity failure;\n'

    full_text += TEXT_3
    return full_text


tests_num = int(input("How many tests do you want to run? "))

out_path = "generated/"
try:
    os.mkdir(out_path)
except FileExistsError:
    pass

for test_count in range(tests_num):
    with open(out_path + "test_" + str(test_count+1) + ".vhd", "w") as file:
        input_list = generate_input(get_size())
        output_list = calculate_output(input_list)
        text = generate_text(input_list, output_list)
        file.write(text)
