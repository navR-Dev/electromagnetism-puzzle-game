import numpy as np
import pyopencl as cl

def compute_fields(charges, charge_vals, loops, width, height):
    spacing = 20
    size_x = width // spacing
    size_y = height // spacing
    field = np.zeros((size_y, size_x, 2), dtype=np.float32)

    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

    charges_np = np.array([(*p, v) for p, v in zip(charges, charge_vals)], dtype=np.float32) if charges else np.zeros((1, 3), dtype=np.float32)
    loops_np = np.array([(*p,) for p in loops], dtype=np.float32) if loops else np.zeros((1, 2), dtype=np.float32)

    mf = cl.mem_flags
    field_buf = cl.Buffer(ctx, mf.WRITE_ONLY, field.nbytes)
    charges_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=charges_np)
    loops_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=loops_np)

    kernel_code = """
    __kernel void compute_field(
        __global float *field,
        __global const float *charges,
        int num_charges,
        __global const float *loops,
        int num_loops,
        int width,
        int height,
        int spacing
    ) {
        int x = get_global_id(0);
        int y = get_global_id(1);
        int idx = (y * width + x) * 2;

        float fx = 0.0f;
        float fy = 0.0f;

        for (int i = 0; i < num_charges; i++) {
            float cx = charges[i*3];
            float cy = charges[i*3+1];
            float val = charges[i*3+2];

            float dx = x * spacing - cx;
            float dy = y * spacing - cy;
            float dist_sq = dx*dx + dy*dy + 10.0f;
            float factor = val / dist_sq;

            fx += factor * dx;
            fy += factor * dy;
        }

        for (int i = 0; i < num_loops; i++) {
            float lx = loops[i*2];
            float ly = loops[i*2+1];

            float dx = x * spacing - lx;
            float dy = y * spacing - ly;
            float dist_sq = dx*dx + dy*dy + 10.0f;

            fx += -dy / dist_sq;
            fy += dx / dist_sq;
        }

        field[idx] = fx;
        field[idx+1] = fy;
    }
    """

    prg = cl.Program(ctx, kernel_code).build()
    prg.compute_field(
        queue, (size_x, size_y), None,
        field_buf,
        charges_buf,
        np.int32(len(charges) if charges else 0),
        loops_buf,
        np.int32(len(loops) if loops else 0),
        np.int32(size_x),
        np.int32(size_y),
        np.int32(spacing)
    )

    cl.enqueue_copy(queue, field, field_buf).wait()
    return field
