import numpy as np
try:
    import pyopencl as cl
    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False

# OpenCL kernel for field computation
FIELD_KERNEL = """
__kernel void compute_field_grid(
    __global const float2 *charges,
    __global const float *charge_vals,
    __global const float2 *loops,
    const int num_charges,
    const int num_loops,
    const int size_x,
    const int size_y,
    const int spacing,
    const float charge_val,
    __global float2 *field)
{
    int x = get_global_id(0);
    int y = get_global_id(1);
    if (x >= size_x || y >= size_y) return;

    float px = x * spacing;
    float py = y * spacing;
    float fx = 0.0f;
    float fy = 0.0f;
    const float k = 1000.0f;
    const float max_dist_sq = 40000.0f; // 200 pixels squared

    // Electric field from charges
    for (int i = 0; i < num_charges; i++) {
        float dx = px - charges[i].x;
        float dy = py - charges[i].y;
        float dist_sq = dx*dx + dy*dy + 5.0f;
        if (dist_sq <= max_dist_sq) {
            float dist = sqrt(dist_sq);
            float e_strength = k * charge_val * charge_vals[i] / dist_sq;
            fx += e_strength * dx / dist;
            fy += e_strength * dy / dist;
        }
    }

    // Magnetic field from loops
    for (int i = 0; i < num_loops; i++) {
        float dx = px - loops[i].x;
        float dy = py - loops[i].y;
        float dist_sq = dx*dx + dy*dy + 5.0f;
        if (dist_sq <= max_dist_sq) {
            float b_strength = 100.0f / dist_sq;
            fx += -b_strength * dy;
            fy += b_strength * dx;
        }
    }

    field[y * size_x + x] = (float2)(fx, fy);
}
__kernel void compute_field_point(
    __global const float2 *charges,
    __global const float *charge_vals,
    __global const float2 *loops,
    const int num_charges,
    const int num_loops,
    const float px,
    const float py,
    const float charge_val,
    __global float *result)
{
    float fx = 0.0f;
    float fy = 0.0f;
    const float k = 1000.0f;
    const float max_dist_sq = 40000.0f; // 200 pixels squared

    for (int i = 0; i < num_charges; i++) {
        float dx = px - charges[i].x;
        float dy = py - charges[i].y;
        float dist_sq = dx*dx + dy*dy + 5.0f;
        if (dist_sq <= max_dist_sq) {
            float dist = sqrt(dist_sq);
            float e_strength = k * charge_val * charge_vals[i] / dist_sq;
            fx += e_strength * dx / dist;
            fy += e_strength * dy / dist;
        }
    }

    for (int i = 0; i < num_loops; i++) {
        float dx = px - loops[i].x;
        float dy = py - loops[i].y;
        float dist_sq = dx*dx + dy*dy + 5.0f;
        if (dist_sq <= max_dist_sq) {
            float b_strength = 100.0f / dist_sq;
            fx += -b_strength * dy;
            fy += b_strength * dx;
        }
    }

    result[0] = fx;
    result[1] = fy;
}
"""

def get_opencl_context():
    if not OPENCL_AVAILABLE:
        return None, None
    platforms = cl.get_platforms()
    if not platforms:
        return None, None
    # Prefer CPU for parallelism
    for platform in platforms:
        devices = platform.get_devices(cl.device_type.CPU)
        if devices:
            ctx = cl.Context(devices)
            queue = cl.CommandQueue(ctx, devices[0])
            return ctx, queue
    # Fallback to GPU
    for platform in platforms:
        devices = platform.get_devices(cl.device_type.GPU)
        if devices:
            ctx = cl.Context(devices)
            queue = cl.CommandQueue(ctx, devices[0])
            return ctx, queue
    return None, None

# Initialize OpenCL
OPENCL_CTX, OPENCL_QUEUE = get_opencl_context()
OPENCL_PRG = cl.Program(OPENCL_CTX, FIELD_KERNEL).build() if OPENCL_CTX else None

def compute_field_grid(charges, charge_vals, loops, width, height):
    spacing = 20
    size_x = width // spacing
    size_y = height // spacing
    field = np.zeros((size_y, size_x, 2), dtype=np.float32)

    if OPENCL_AVAILABLE and OPENCL_CTX:
        # PyOpenCL: Parallel grid computation
        num_charges = len(charges)
        num_loops = len(loops)
        if num_charges == 0 and num_loops == 0:
            return field  # No forces if no charges or loops

        charges_np = np.array(charges, dtype=np.float32) if num_charges else np.zeros((1, 2), dtype=np.float32)
        charge_vals_np = np.array(charge_vals, dtype=np.float32) if num_charges else np.zeros(1, dtype=np.float32)
        loops_np = np.array(loops, dtype=np.float32) if num_loops else np.zeros((1, 2), dtype=np.float32)
        field_np = np.zeros((size_y * size_x, 2), dtype=np.float32)

        mf = cl.mem_flags
        charges_buf = cl.Buffer(OPENCL_CTX, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=charges_np)
        charge_vals_buf = cl.Buffer(OPENCL_CTX, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=charge_vals_np)
        loops_buf = cl.Buffer(OPENCL_CTX, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=loops_np)
        field_buf = cl.Buffer(OPENCL_CTX, mf.WRITE_ONLY, field_np.nbytes)

        OPENCL_PRG.compute_field_grid(
            OPENCL_QUEUE, (size_x, size_y), None,
            charges_buf, charge_vals_buf, loops_buf,
            np.int32(num_charges), np.int32(num_loops),
            np.int32(size_x), np.int32(size_y), np.int32(spacing),
            np.float32(1.0), field_buf
        )
        cl.enqueue_copy(OPENCL_QUEUE, field_np, field_buf)
        OPENCL_QUEUE.finish()
        field = field_np.reshape(size_y, size_x, 2)
        return field

    # NumPy: CPU fallback
    for y in range(size_y):
        for x in range(size_x):
            px, py = x * spacing, y * spacing
            fx, fy = compute_field_at_point((px, py), charges, charge_vals, loops, 1.0)
            field[y, x] = [fx, fy]
    return field

def compute_field_at_point(pos, charges, charge_vals, loops, charge_val):
    px, py = pos
    fx, fy = 0.0, 0.0
    k = 1000.0
    max_dist_sq = 40000.0  # 200 pixels squared

    if OPENCL_AVAILABLE and OPENCL_CTX:
        # PyOpenCL: Single-point computation
        num_charges = len(charges)
        num_loops = len(loops)
        if num_charges == 0 and num_loops == 0:
            return fx, fy  # No forces if no charges or loops

        charges_np = np.array(charges, dtype=np.float32) if num_charges else np.zeros((1, 2), dtype=np.float32)
        charge_vals_np = np.array(charge_vals, dtype=np.float32) if num_charges else np.zeros(1, dtype=np.float32)
        loops_np = np.array(loops, dtype=np.float32) if num_loops else np.zeros((1, 2), dtype=np.float32)
        
        mf = cl.mem_flags
        charges_buf = cl.Buffer(OPENCL_CTX, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=charges_np)
        charge_vals_buf = cl.Buffer(OPENCL_CTX, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=charge_vals_np)
        loops_buf = cl.Buffer(OPENCL_CTX, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=loops_np)
        result_buf = cl.Buffer(OPENCL_CTX, mf.WRITE_ONLY, np.array([0.0, 0.0], dtype=np.float32).nbytes)

        OPENCL_PRG.compute_field_point(
            OPENCL_QUEUE, (1,), None,
            charges_buf, charge_vals_buf, loops_buf,
            np.int32(num_charges), np.int32(num_loops),
            np.float32(px), np.float32(py), np.float32(charge_val),
            result_buf
        )
        result = np.empty(2, dtype=np.float32)
        cl.enqueue_copy(OPENCL_QUEUE, result, result_buf)
        OPENCL_QUEUE.finish()
        return result[0], result[1]

    # NumPy: CPU fallback
    for (cx, cy), val in zip(charges, charge_vals):
        dx = px - cx
        dy = py - cy
        dist_sq = dx*dx + dy*dy + 5.0
        if dist_sq <= max_dist_sq:
            dist = np.sqrt(dist_sq)
            e_strength = k * charge_val * val / dist_sq
            fx += e_strength * dx / dist
            fy += e_strength * dy / dist

    for lx, ly in loops:
        dx = px - lx
        dy = py - ly
        dist_sq = dx*dx + dy*dy + 5.0
        if dist_sq <= max_dist_sq:
            b_strength = 100.0 / dist_sq
            fx += -b_strength * dy
            fy += b_strength * dx

    return fx, fy