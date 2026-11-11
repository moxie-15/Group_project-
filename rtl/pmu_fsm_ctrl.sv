// ============================================================================
// File: pmu_fsm_ctrl.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Canonical Three-Process Moore Finite State Machine (FSM).
//              Process 1: Sequential state register (always_ff).
//              Process 2: Combinational next-state logic (always_comb).
//              Process 3: Pure Moore combinational output logic (always_comb).
//              Strictly follows IEEE digital design standards with zero
//              input-dependent outputs and zero inferred latches.
// ============================================================================

`timescale 1ns / 1ps

module pmu_fsm_ctrl
    import fdi_pkg::*;
(
    input  logic              clk,
    input  logic              rst_n,

    // Upstream Handshake
    input  logic              data_valid,
    output logic              data_ready,

    // Datapath Handshakes & Completion Signals
    input  logic              mahal_done,
    input  logic              channel_last,  // High when current channel is last channel (N-1)

    // Moore Output Control Strobes (Derived ONLY from current_state)
    output logic              latch_sample_o,
    output logic              preprocess_en_o,
    output logic              mahal_start_o,
    output logic              cusum_en_o,
    output logic              decision_en_o,
    output logic              bram_we_o,
    output logic              chan_advance_o,
    output logic              frame_done_o,
    output fsm_state_t        current_state_o
);

    // State Variables
    fsm_state_t current_state, next_state;

    // ========================================================================
    // Process 1: Sequential State Register with Asynchronous Active-Low Reset
    // ========================================================================
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= FSM_IDLE;
        end else begin
            current_state <= next_state;
        end
    end

    // ========================================================================
    // Process 2: Combinational Next-State Transition Logic
    // Evaluates current_state and input conditions to determine next_state
    // ========================================================================
    always_comb begin
        // Default assignment avoids latches
        next_state = current_state;

        case (current_state)
            FSM_IDLE: begin
                if (data_valid) begin
                    next_state = FSM_CAPTURE;
                end else begin
                    next_state = FSM_IDLE;
                end
            end

            FSM_CAPTURE: begin
                next_state = FSM_PREPROCESS;
            end

            FSM_PREPROCESS: begin
                next_state = FSM_MAHALANOBIS;
            end

            FSM_MAHALANOBIS: begin
                // Wait for multi-cycle Mahalanobis calculation to finish
                if (mahal_done) begin
                    next_state = FSM_CUSUM;
                end else begin
                    next_state = FSM_MAHALANOBIS;
                end
            end

            FSM_CUSUM: begin
                next_state = FSM_DECISION;
            end

            FSM_DECISION: begin
                next_state = FSM_STORE_RESULT;
            end

            FSM_STORE_RESULT: begin
                next_state = FSM_NEXT_CHANNEL;
            end

            FSM_NEXT_CHANNEL: begin
                // If all channels in current frame are processed, return to IDLE
                if (channel_last) begin
                    next_state = FSM_IDLE;
                end else begin
                    next_state = FSM_CAPTURE; // Process next channel in vector
                end
            end

            default: next_state = FSM_IDLE;
        endcase
    end

    // ========================================================================
    // Process 3: Pure Moore Combinational Output Logic
    // STRICT MOORE PROPERTY: Outputs are functions solely of current_state
    // ========================================================================
    always_comb begin
        // Default safe values for all output strobes
        data_ready      = 1'b0;
        latch_sample_o  = 1'b0;
        preprocess_en_o = 1'b0;
        mahal_start_o   = 1'b0;
        cusum_en_o      = 1'b0;
        decision_en_o   = 1'b0;
        bram_we_o       = 1'b0;
        chan_advance_o  = 1'b0;
        frame_done_o    = 1'b0;

        case (current_state)
            FSM_IDLE: begin
                data_ready = 1'b1; // Ready to accept new incoming sample frame
            end

            FSM_CAPTURE: begin
                latch_sample_o = 1'b1; // Latch input PMU vector into registers
            end

            FSM_PREPROCESS: begin
                preprocess_en_o = 1'b1; // Perform mean-centering and scaling
            end

            FSM_MAHALANOBIS: begin
                mahal_start_o = 1'b1; // Trigger Mahalanobis matrix engine
            end

            FSM_CUSUM: begin
                cusum_en_o = 1'b1; // Step CUSUM positive and negative filters
            end

            FSM_DECISION: begin
                decision_en_o = 1'b1; // Evaluate threshold crossing and alarms
            end

            FSM_STORE_RESULT: begin
                bram_we_o = 1'b1; // Commit updated channel state to BRAM
            end

            FSM_NEXT_CHANNEL: begin
                chan_advance_o = 1'b1; // Increment channel pointer
                frame_done_o   = 1'b1; // Assert frame completion strobe
            end

            default: ;
        endcase
    end

    assign current_state_o = current_state;

endmodule
