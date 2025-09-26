import json
import ezdxf
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

def json_to_dxf(json_file: str, dxf_file: str):
    with open(json_file, "r") as f:
        data = json.load(f)

    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    for entity in data.get("entities", []):
        etype = entity.get("type")
        params = entity.get("params", {})

        if etype == "LINE":
            msp.add_line(params["start_point"], params["end_point"])

        elif etype == "CIRCLE":
            msp.add_circle(center=params["center"], radius=params["radius"])

        elif etype == "ARC":
            msp.add_arc(
                center=params["center"],
                radius=params["radius"],
                start_angle=params["start_angle"],
                end_angle=params["end_angle"]
            )

        elif etype == "ANGULAR_DIMENSION":
            dim = msp.add_arc_dim_cra(
                center=params["center"],
                radius=params["radius"],
                start_angle=params["start_angle"],
                end_angle=params["end_angle"],
                distance=params.get("distance", 2),
                dimstyle=params.get("dimstyle", "EZ_CURVED"),
            )
            dim.render()

        else:
            print(f"Unsupported entity type: {etype}")

    doc.saveas(dxf_file)
    print(f"DXF file saved as {dxf_file}")

    # -------- Visualization --------
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    plt.show()


if __name__ == "__main__":
    json_to_dxf("fifthTask.json", "sixthTask.dxf")