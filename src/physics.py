import numpy as np

try:
    import pyopencl as cl
    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False

if OPENCL_AVAILABLE:
    FIELD_KERNEL = """
    __kernel void compute_field_grid(
        __global float2 *charges,
        __global float *charge_vals,
        __global float2 *loops,
        int num_charges,
        int num_loops,
        int size_x,
        int size_y,
        int spacing,
        float charge_val,
        int compute_electric,
        int compute_magnetic,
        __global float2 *field
    ) {
        int x = get_global_id(0);
        int y = get_global_id(1);
        if (x >= size_x || y >= size_y) return;

        float px = x * spacing;
        float py = y * spacing;
        float fx = 0.0f;
        float fy = 0.0f;
        float k = 1000.0f;
        float max_dist_sq = 40000.0f;

        if (compute_electric) {
            for (int i = 0; i < num_charges; i++) {
                float dx = charges[i].x - px;
                float dy = charges[i].y - py;
                float dist_sq = dx * dx + dy * dy + 5.0f;
                if (dist_sq < max_dist_sq) {
                    float dist = sqrt(dist_sq);
                    float e_strength = (k * charge_val * charge_vals[i]) / dist_sq;
                    fx += e_strength * (dx / dist);
                    fy += e_strength * (dy / dist);
                }
            }
        }

        if (compute_magnetic) {
            for (int i = 0; i < num_loops; i++) {
                float dx = loops[i].x - px;
                float dy = loops[i].y - py;
                float dist_sq = dx * dx + dy * dy + 5.0f;
                if (dist_sq < max_dist_sq) {
                    float b_strength = 100.0f / dist_sq;
                    fx += -b_strength * dy;
                    fy += b_strength * dx;
                }
            }
        }

        field[y * size_x + x] = (float2)(fx, fy);
    }

    __kernel void compute_field_point(
        __global float2 *charges,
        __global float *charge_vals,
        __global float2 *loops,
        int num_charges,
        int num_loops,
        float px,
        float py,
        float charge_val,
        float vx,
        float vy,
        __global float2 *result
    ) {
        float fx = 0.0f;
        float fy = 0.0f;
        float k = 1000.0f;
        float kb = 100.0f;
        float max_dist_sq = 40000.0f;

        for (int i = 0; i < num_charges; i++) {
            float dx = charges[i].x - px;
            float dy = charges[i].y - py;
            float dist_sq = dx * dx + dy * dy + 5.0f;
            if (dist_sq < max_dist_sq) {
                float dist = sqrt(dist_sq);
                float e_strength = (k * charge_val * charge_vals[i]) / dist_sq;
                fx += e_strength * (dx / dist);
                fy += e_strength * (dy / dist);
            }
        }

        for (int i = 0; i < num_loops; i++) {
            float dx = loops[i].x - px;
            float dy = loops[i].y - py;
            float dist_sq = dx * dx + dy * dy + 5.0f;
            if (dist_sq < max_dist_sq) {
                float bz = kb / dist_sq;
                fx += -charge_val * bz * vy;
                fy += charge_val * bz * vx;
            }
        }

        result[0] = (float2)(fx, fy);
    }
    """

def get_opencl_context():
    if not OPENCL_AVAILABLE:
        print("OpenCL not available, falling back to NumPy")
        return None, None
    try:
        platforms = cl.get_platforms()
        if not platforms:
            print("No OpenCL platforms found, falling back to NumPy")
            return None, None

        # Prioritize GPU devices (including iGPUs)
        for platform in platforms:
            devices = platform.get_devices(cl.device_type.GPU)
            if devices:
                ctx = cl.Context(devices)
                queue = cl.CommandQueue(ctx, devices[0])
                print(f"Using GPU device: {devices[0].name}")
                return ctx, queue

        # Fallback: No GPU devices found
        print("No GPU devices found, falling back to NumPy")
        return None, None

    except Exception as e:
        print(f"OpenCL initialization failed: {e}, falling back to NumPy")
        return None, None

OPENCL_CTX, OPENCL_QUEUE = get_opencl_context()

if OPENCL_AVAILABLE and OPENCL_CTX is not None:
    OPENCL_PRG = cl.Program(OPENCL_CTX, FIELD_KERNEL).build()

def compute_field_grid(charges, charge_vals, loops, width, height, compute_electric=True, compute_magnetic=True):
    spacing = 20
    size_x = width // spacing
    size_y = height // spacing
    field_np = np.zeros((size_y, size_x, 2), dtype=np.float32)

    if not charges:
        charges = [(0, 0)]
        charge_vals = [0.0]
    if not loops:
        loops = [(0, 0)]

    num_charges = len(charges)
    num_loops = len(loops)
    charges_np = np.array(charges, dtype=np.float32)
    charge_vals_np = np.array(charge_vals, dtype=np.float32)
    loops_np = np.array(loops, dtype=np.float32)

    if OPENCL_AVAILABLE and OPENCL_CTX is not None:
        charges_buf = cl.Buffer(OPENCL_CTX, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=charges_np)
        charge_vals_buf = cl.Buffer(OPENCL_CTX, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=charge_vals_np)
        loops_buf = cl.Buffer(OPENCL_CTX, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=loops_np)
        field_buf = cl.Buffer(OPENCL_CTX, cl.mem_flags.WRITE_ONLY, field_np.nbytes)

        OPENCL_PRG.compute_field_grid(
            OPENCL_QUEUE, (size_x, size_y), None,
            charges_buf, charge_vals_buf, loops_buf,
            np.int32(num_charges), np.int32(num_loops),
            np.int32(size_x), np.int32(size_y), np.int32(spacing),
            np.float32(1.0), np.int32(compute_electric), np.int32(compute_magnetic),
            field_buf
        )

        cl.enqueue_copy(OPENCL_QUEUE, field_np, field_buf).wait()
        return field_np

    k = 1000.0
    for y in range(size_y):
        for x in range(size_x):
            fx, fy = compute_field_at_point(
                [x * spacing, y * spacing], charges, charge_vals, loops,
                charge_val=1.0, velocity=(0.0, 0.0),
                compute_electric=compute_electric, compute_magnetic=compute_magnetic
            )
            field_np[y, x] = [fx, fy]
    return field_np

def compute_field_at_point(pos, charges, charge_vals, loops, charge_val, velocity=(0.0, 0.0), compute_electric=True, compute_magnetic=True):
    px, py = pos
    vx, vy = velocity

    if not charges:
        charges = [(0, 0)]
        charge_vals = [0.0]
    if not loops:
        loops = [(0, 0)]

    num_charges = len(charges)
    num_loops = len(loops)
    charges_np = np.array(charges, dtype=np.float32)
    charge_vals_np = np.array(charge_vals, dtype=np.float32)
    loops_np = np.array(loops, dtype=np.float32)
    result_np = np.zeros(2, dtype=np.float32)

    if OPENCL_AVAILABLE and OPENCL_CTX is not None:
        charges_buf = cl.Buffer(OPENCL_CTX, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=charges_np)
        charge_vals_buf = cl.Buffer(OPENCL_CTX, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=charge_vals_np)
        loops_buf = cl.Buffer(OPENCL_CTX, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=loops_np)
        result_buf = cl.Buffer(OPENCL_CTX, cl.mem_flags.WRITE_ONLY, result_np.nbytes)

        OPENCL_PRG.compute_field_point(
            OPENCL_QUEUE, (1,), None,
            charges_buf, charge_vals_buf, loops_buf,
            np.int32(num_charges), np.int32(num_loops),
            np.float32(px), np.float32(py), np.float32(charge_val),
            np.float32(vx), np.float32(vy),
            result_buf
        )

        cl.enqueue_copy(OPENCL_QUEUE, result_np, result_buf).wait()
        fx, fy = result_np[0], result_np[1]
        # Fix reversed attraction: Negate OpenCL forces to restore correct repulsion/attraction
        fx, fy = -fx, -fy
        print(f"OpenCL forces: fx={fx:.2f}, fy={fy:.2f}, charge_val={charge_val}, charges={charge_vals}")
        return fx, fy

    fx = 0.0
    fy = 0.0
    k = 1000.0
    kb = 100.0
    max_dist_sq = 40000.0

    if compute_electric:
        for i in range(num_charges):
            dx = charges[i][0] - px
            dy = charges[i][1] - py
            dist_sq = dx * dx + dy * dy + 5.0
            if dist_sq < max_dist_sq:
                dist = np.sqrt(dist_sq)
                e_strength = (k * charge_val * charge_vals[i]) / dist_sq
                fx += e_strength * (dx / dist)
                fy += e_strength * (dy / dist)

    if compute_magnetic:
        for i in range(num_loops):
            dx = loops[i][0] - px
            dy = loops[i][1] - py
            dist_sq = dx * dx + dy * dy + 5.0
            if dist_sq < max_dist_sq:
                bz = kb / dist_sq
                fx += -charge_val * bz * vy
                fy += charge_val * bz * vx

    print(f"NumPy forces: fx={fx:.2f}, fy={fy:.2f}, charge_val={charge_val}, charges={charge_vals}")
    return fx, fy