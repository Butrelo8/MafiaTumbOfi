# fitlib.py: shared pieces of the parts assembly (fit.py). Every mesh is handled in the Blender frame of the Mixamo upload
# (GLB Y-up -> Z-up, 1.0 m tall, feet on z = 0, facing -Y). Transforms are 4x4 similarities (uniform scale).
import numpy as np, trimesh
from scipy.spatial import cKDTree


def load_glb(path):
    """Vertices (Blender frame, GLB units), faces, per-vertex colour sampled from the texture."""
    m = trimesh.load(path, force="mesh", process=False)
    V = np.asarray(m.vertices, float); V = np.c_[V[:, 0], -V[:, 2], V[:, 1]]
    try:
        C = np.asarray(m.visual.to_color().vertex_colors)[:, :3].astype(float)
    except Exception:
        C = np.full((len(V), 3), 128.0)
    return V, np.asarray(m.faces), C


def apply(T, P):
    return P @ T[:3, :3].T + T[:3, 3]


def umeyama(A, B):
    """Similarity T with T(A) ~ B (least squares, uniform scale)."""
    ma, mb = A.mean(0), B.mean(0); a, b = A - ma, B - mb
    U, S, Vt = np.linalg.svd(b.T @ a / len(A))
    D = np.eye(3); D[2, 2] = np.sign(np.linalg.det(U @ Vt))
    R = U @ D @ Vt; s = (S * np.diag(D)).sum() / (a ** 2).sum(1).mean()
    T = np.eye(4); T[:3, :3] = s * R; T[:3, 3] = mb - s * R @ ma
    return T


def bbox_init(src, tgt, axes=(0, 1, 2), scale_axis=None, anchor=("c", "c", "min")):
    """Scale from one axis' extent (or the mean of all), then line up each axis by centre or min."""
    ls, hs, lt, ht = src.min(0), src.max(0), tgt.min(0), tgt.max(0)
    ext_s, ext_t = hs - ls, ht - lt
    s = ext_t[scale_axis] / ext_s[scale_axis] if scale_axis is not None else np.mean(ext_t / ext_s)
    T = np.eye(4); T[:3, :3] *= s
    for k, a in enumerate(anchor):
        ps = (ls[k] + hs[k]) / 2 if a == "c" else ls[k] if a == "min" else hs[k]
        pt = (lt[k] + ht[k]) / 2 if a == "c" else lt[k] if a == "min" else ht[k]
        T[k, 3] = pt - s * ps
    return T


def icp(src, tgt, T, iters=60, trim=0.85, scale=True, both=False):
    """Trimmed ICP: each target point pulls its nearest moved source point (and, with both=True, each source point
    its nearest target point). Returns T and the final distances target->source (GLB units)."""
    tt = cKDTree(tgt)
    for it in range(iters):
        P = apply(T, src); ts = cKDTree(P)
        d, j = ts.query(tgt); keep = d <= np.quantile(d, trim)
        A, B = src[j[keep]], tgt[keep]
        if both:
            d2, k2 = tt.query(P); k = d2 <= np.quantile(d2, trim)
            A = np.r_[A, src[k]]; B = np.r_[B, tgt[k2[k]]]
        Tn = umeyama(A, B)
        if not scale:
            s = np.cbrt(np.linalg.det(Tn[:3, :3])); Tn[:3, :3] /= s
            Tn[:3, 3] = B.mean(0) - Tn[:3, :3] @ A.mean(0)
        if np.abs(Tn - T).max() < 1e-7: T = Tn; break
        T = Tn
    d, _ = cKDTree(apply(T, src)).query(tgt)
    return T, d
