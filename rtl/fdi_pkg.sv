// ============================================================================
// File: fdi_pkg.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Global package defining architectural dimensions, Q1.15 signed
//              fixed-point types, intermediate widths, and saturation helpers.
// ============================================================================

package fdi_pkg;

    // ------------------------------------------------------------------------
    // System Dimensions
    // ------------------------------------------------------------------------
    parameter int N_CHANNELS      = 4;   // 4-dimensional PMU measurement vector
    parameter int MAX_CHANNELS    = 8;   // Scalable up to 8 channels in BRAM
    parameter int CHANNEL_BITS    = 3;   // clog2(MAX_CHANNELS)

    // ------------------------------------------------------------------------
    // Q1.15 Fixed-Point Datapath Definitions
    // 1 Sign bit, 15 Fractional bits
    // Range: [-1.0, +0.999969482421875], LSB = 2^-15 = 3.0517578125e-5
    // ------------------------------------------------------------------------
    parameter int Q15_WIDTH       = 16;
    parameter int Q15_FRAC        = 15;
    parameter int Q15_ONE         = 16'sh7FFF; // +0.999969 (~1.0)
    parameter int Q15_ZERO        = 16'sh0000; // 0.0
    parameter int Q15_MINUS_ONE   = 16'sh8000; // -1.0

    // Full-precision intermediate multiplication (Q1.15 x Q1.15 = Q2.30)
    parameter int PROD_WIDTH      = 32;
    parameter int PROD_FRAC       = 30;

    // Multi-cycle / Matrix Accumulator (Guard bits for N=4 sum: +2 bits -> 34-bit)
    parameter int ACCUM_GUARD     = 2;
    parameter int ACCUM_WIDTH     = PROD_WIDTH + ACCUM_GUARD; // 34-bit

    // ------------------------------------------------------------------------
    // Typedefs for Strongly-Typed Datapath
    // ------------------------------------------------------------------------
    typedef logic signed [Q15_WIDTH-1:0]    q15_t;        // Signed Q1.15 (16-bit)
    typedef logic signed [PROD_WIDTH-1:0]   prod_q2_30_t; // Signed Q2.30 (32-bit)
    typedef logic signed [ACCUM_WIDTH-1:0]  accum_q4_30_t;// Signed Q4.30 (34-bit)

    // Vector and Matrix Structures
    typedef q15_t [N_CHANNELS-1:0]                 pmu_vec_t;
    typedef q15_t [N_CHANNELS-1:0][N_CHANNELS-1:0] pmu_mat_t;

    // ------------------------------------------------------------------------
    // PMU Per-Channel BRAM State Record
    // Stored in on-chip Block RAM
    // ------------------------------------------------------------------------
    typedef struct packed {
        q15_t        s_pos;          // Positive CUSUM accumulator state (Q1.15)
        q15_t        s_neg;          // Negative CUSUM accumulator state (Q1.15)
        q15_t        last_sample;    // Previous filtered sample (Q1.15)
        logic        spatial_alert;  // Latched Mahalanobis alert
        logic        temporal_alert; // Latched CUSUM alert
        logic        fdi_alert;      // Latched combined alert
        logic [9:0]  alert_count;    // Anomaly event counter (10 bits)
    } pmu_channel_state_t;

    // ------------------------------------------------------------------------
    // Moore FSM State Enumeration (Three-Process Moore Controller)
    // ------------------------------------------------------------------------
    typedef enum logic [2:0] {
        FSM_IDLE         = 3'b000,
        FSM_CAPTURE      = 3'b001,
        FSM_PREPROCESS   = 3'b010,
        FSM_MAHALANOBIS  = 3'b011,
        FSM_CUSUM        = 3'b100,
        FSM_DECISION     = 3'b101,
        FSM_STORE_RESULT = 3'b110,
        FSM_NEXT_CHANNEL = 3'b111
    } fsm_state_t;

    // ------------------------------------------------------------------------
    // Arithmetic Helper: Q1.15 Multiplication with Rounding & Saturation
    // In DSP arithmetic: (a * b) produces 32 bits with 30 fractional bits.
    // To extract Q1.15: add rounding bit (bit 14), then select bits [30:15].
    // Handle corner case: -1.0 * -1.0 = +1.0 (overflows Q1.15 -> clamp to +0.9999)
    // ------------------------------------------------------------------------
    function automatic q15_t q15_mult(input q15_t a, input q15_t b);
        logic signed [31:0] full_prod;
        logic signed [31:0] rounded_prod;
        q15_t result;

        full_prod = logic signed [31:0]'(a) * logic signed [31:0]'(b);

        // Corner case: (-1.0) * (-1.0) = 0x8000 * 0x8000 = 0x40000000
        if (a == 16'sh8000 && b == 16'sh8000) begin
            result = 16'sh7FFF; // Saturate to +0.999969
        end else begin
            // Convergent/half-up rounding: add 1 to bit 14
            rounded_prod = full_prod + 32'sh0000_4000;
            // Bits [30:15] represent Q1.15
            result = rounded_prod[30:15];
        end

        return result;
    endfunction

    // ------------------------------------------------------------------------
    // Arithmetic Helper: Q1.15 Addition with Saturation
    // Clamps to [-1.0, +0.999969] to eliminate silent integer wraparound
    // ------------------------------------------------------------------------
    function automatic q15_t q15_add_sat(input q15_t a, input q15_t b);
        logic signed [16:0] sum;
        q15_t result;

        sum = logic signed [16:0]'(a) + logic signed [16:0]'(b);

        if (sum > 17'sh07FFF) begin
            result = 16'sh7FFF; // Positive saturation
        end else if (sum < -17'sh08000) begin
            result = 16'sh8000; // Negative saturation
        end else begin
            result = sum[15:0];
        end

        return result;
    endfunction

    // ------------------------------------------------------------------------
    // Arithmetic Helper: Q1.15 Subtraction with Saturation
    // ------------------------------------------------------------------------
    function automatic q15_t q15_sub_sat(input q15_t a, input q15_t b);
        logic signed [16:0] diff;
        q15_t result;

        diff = logic signed [16:0]'(a) - logic signed [16:0]'(b);

        if (diff > 17'sh07FFF) begin
            result = 16'sh7FFF;
        end else if (diff < -17'sh08000) begin
            result = 16'sh8000;
        end else begin
            result = diff[15:0];
        end

        return result;
    endfunction

endpackage: fdi_pkg
