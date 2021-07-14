class Patch:
    def __init__(self, node_id, patch_type, operation, payload, issuer=None):
        self.issuer = issuer

        self.data = [
            node_id,
            patch_type,
            operation,
            *payload,
        ]

    def __repr__(self):
        return '<Patch({}, {}, {})>'.format(
            self.data[0],
            self.data[1],
            self.data[2],
        )


class PatchStack:
    def __init__(self):
        self.patches = []

    def add_patch(self, *args, **kwargs):
        self.patches.append(Patch(*args, **kwargs))

    def has_patches(self):
        return bool(self.patches)

    def get_patches(self):
        patch_data = []

        for patch in self.patches:
            patch_data.append(patch)

        return patch_data

    def clear(self):
        self.patches.clear()
