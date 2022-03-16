----------------------------------------------------------------------------------
-- Authors: Montanari Tommaso and Negri Riccardo
-- 
-- Module Name: project_reti_logiche - Behavioral
-- Project Name: 
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity project_reti_logiche is
    port (
        i_clk : in std_logic;
        i_rst : in std_logic;
        i_start : in std_logic;
        i_data : in std_logic_vector(7 downto 0);
        o_address : out std_logic_vector(15 downto 0);
        o_done : out std_logic;
        o_en  : out std_logic;
        o_we : out std_logic;
        o_data : out std_logic_vector (7 downto 0)
    );
end project_reti_logiche;

architecture Behavioral of project_reti_logiche is

type state_type is (START, WAIT_WORDS_NUMBER, FETCH_WORDS_NUMBER, CALL_READ, WAIT_READ, FETCH_READ, ENCODER_1_TO_2, DONE, WRITE, AFTER_DONE);
type internal_state_type is (S00, S01, S10, S11);

signal state : state_type;
signal internal_state : internal_state_type;
signal finished_reading : boolean;
signal w_word_index, shift : integer range 0 to 7;
signal w_word, words_number, words_left, z_word : std_logic_vector(7 downto 0);
signal read_addr, write_addr : std_logic_vector(15 downto 0);

begin
    process(i_clk, i_rst)
    begin
        if i_rst = '1' then
            state <= START;
            o_done <= '0';
            
        elsif rising_edge(i_clk) then
            case state is
                when START =>
                    if(i_start='1') then
                        internal_state <= S00;
                        finished_reading <= false;
                        write_addr <= "0000001111101000";
                        -- GET_WORDS_NUMBER
                        o_en <= '1';
                        o_we <= '0';
                        o_address <= (others => '0');
                        read_addr <= "0000000000000001";
                        state <= WAIT_WORDS_NUMBER;
                    end if;
                
                when WAIT_WORDS_NUMBER =>
                    o_en <= '0';
                    state <= FETCH_WORDS_NUMBER;
                    
                when FETCH_WORDS_NUMBER =>
                    words_left <= i_data;
                    if (i_data = 0) then
                        state <= DONE;
                    else
                        state <= CALL_READ;
                    end if;
                    
                when CALL_READ =>
                    o_en <= '1';
                    o_we <= '0';
                    o_address <= read_addr;
                    read_addr <= read_addr + 1;
                    state <= WAIT_READ;
                    
                when WAIT_READ =>
                    o_en <= '0';
                    state <= FETCH_READ;
                    
                when FETCH_READ =>
                    w_word <= i_data;                    
                    -- setup encoder
                    z_word <= "00000000";
                    w_word_index <= 7;
                    shift <= 6;
                    state <= ENCODER_1_TO_2; 
                    
                when ENCODER_1_TO_2 =>
                    o_en <= '0';
                    case internal_state is
                        when S00 =>
                            if w_word(w_word_index) = '0' then
                                z_word(shift+1 downto shift) <= "00";
                                internal_state <= S00;
                            end if;
                            if w_word(w_word_index) = '1' then
                                z_word(shift+1 downto shift) <= "11";
                                internal_state <= S10;
                            end if;
                        when S01 =>
                            if w_word(w_word_index) = '0' then
                                z_word(shift+1 downto shift) <= "11";
                                internal_state <= S00;
                            end if;
                            if w_word(w_word_index) = '1' then
                                z_word(shift+1 downto shift) <= "00";
                                internal_state <= S10;
                            end if;
                        when S10 =>
                            if w_word(w_word_index) = '0' then
                                z_word(shift+1 downto shift) <= "01";
                                internal_state <= S01;
                            end if;
                            if w_word(w_word_index) = '1' then
                                z_word(shift+1 downto shift) <= "10";
                                internal_state <= S11;
                            end if;
                        when S11 =>
                            if w_word(w_word_index) = '0' then
                                z_word(shift+1 downto shift) <= "10";
                                internal_state <= S01;
                            end if;
                            if w_word(w_word_index) = '1' then
                                z_word(shift+1 downto shift) <= "01";
                                internal_state <= S11;
                            end if;
                    end case;
                    
                    shift <= shift-2;
                    
                    if (w_word_index = 4) then
                        w_word_index <= w_word_index - 1;
                        shift <= 6;
                        state <= WRITE;
                    elsif (w_word_index = 0) then                      
                        finished_reading <= true;
                        words_left <= words_left -1;
                        state <= WRITE;
                    else
                        w_word_index <= w_word_index - 1;
                        state <= ENCODER_1_TO_2;
                    end if;
                    
                when WRITE =>
                    o_en <= '1';
                    o_we <= '1';
                    o_address <= write_addr;
                    o_data <= z_word;
                    write_addr <= write_addr + "0000000000000001";
                    
                    if (words_left = 0) then
                        state <= DONE;
                    elsif (finished_reading) then
                        state <= CALL_READ;
                        finished_reading <= false;
                    else
                        z_word <= "00000000";
                        state <= ENCODER_1_TO_2;
                    end if;
                    
                when DONE =>
                    o_en <= '0';
                    o_done <= '1';
                    state <= AFTER_DONE;
                    
                when AFTER_DONE =>
                    if (i_start='0') then
                        o_done <= '0';
                        state <= START;
                    end if;
                
            end case;      
        end if;      
    end process;

end Behavioral;
