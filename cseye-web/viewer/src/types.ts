export interface Extents { xmin: number; xmax: number; ymin: number; ymax: number; }
export interface Story { name: string; elev: number; }
export interface ResultSet { name: string; kind: "case" | "combo"; finished: number | null; extracted: boolean; }

export interface Meta {
  id: string; model: string; path: string; etabs_version: string; units: string;
  locked: boolean; extents: Extents; stories: Story[]; result_sets: ResultSet[];
}

export interface Frame {
  name: string; label: string; story: string; type: string;
  ix: number; iy: number; iz: number; jx: number; jy: number; jz: number; section: string;
}
export interface GridLine { id: string; dir: string; x1: number; y1: number; x2: number; y2: number; visible: number; }
export interface Geometry { frames: Frame[]; grid_lines: GridLine[]; }

export interface PlanColumn {
  name: string; label: string; section: string;
  ix: number; iy: number; iz: number; jx: number; jy: number; jz: number;
  pmin: number | null; pmax: number | null; v2: number | null; v3: number | null; m2: number | null; m3: number | null;
}
export interface Support {
  joint: string; x: number; y: number; z: number;
  fx: number; fy: number; fz: number; mx: number; my: number; mz: number;
  fzmin?: number; fzmax?: number;
}
export interface ModelInfo {
  path: string; name: string; dir: string; size_mb: number; mtime: number; has_results_guess: boolean;
}
