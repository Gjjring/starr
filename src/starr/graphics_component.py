from descartes import PolygonPatch

class GraphicsComponent():

    def __init__(self, color):
        self.color = color
        self.edge_color = 'k'
        self.patch = None

    def update(self, geometry_component, canvas):
        if self.patch is None:
            self.patch = PolygonPatch(geometry_component.polygon,
                                    fc=self.color, ec=self.edge_color)
            #print(geometry_component._position)
            #print(geometry_component.polygon.representative_point())
            canvas.axes.add_patch(self.patch)
        else:
            path = PolygonPatch(geometry_component.polygon,
                                fc=self.color).get_path()
            self.patch._path = path
            self.patch.set_facecolor(self.color)

    def remove(self):
        self.patch.remove()
