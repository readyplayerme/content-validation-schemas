"""
Glasses Validation Schema.

This module defines a Pydantic model for validating an asset of type Glasses. It includes error messages
for validation failures and provides a JSON schema for the model.

Author: Daniel-Ionut Rancea <TechyDaniel@users.noreply.github.com>
Co-authored-by: Olaf Haag <Olaf-Wolf3D@users.noreply.github.com>
Co-authored-by: Ivan Sanandres Gutierrez <IvanRPM@users.noreply.github.com>
"""

from pydantic import ConfigDict, ValidationError

from readyplayerme.asset_validation_schemas import common_mesh
from readyplayerme.asset_validation_schemas.animation import NoAnimation
from readyplayerme.asset_validation_schemas.basemodel import BaseModel
from readyplayerme.asset_validation_schemas.common_texture import TextureSchemaStandard


class Mesh(BaseModel):
    """inspect() creates a 'properties' object. Do not confuse with the 'properties' keyword."""

    properties: list[common_mesh.CommonMesh]
    has_morph_targets: bool
    total_triangle_count: int


class AssetGlasses(BaseModel):
    """Validation schema for asset of type Glasses."""

    model_config = ConfigDict(title="Glasses Asset")

    asset_type: str
    transforms: object
    joints: object
    gltf_errors: object
    scenes: object
    meshes: Mesh
    materials: object
    animations: NoAnimation
    textures: TextureSchemaStandard


# Print the generated JSON schema with indentation
if __name__ == "__main__":
    import logging

    from readyplayerme.asset_validation_schemas.schema_io import write_json

    logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
    # Convert model to JSON schema.
    write_json(AssetGlasses.model_json_schema())

    # Example of validation in Python
    try:
        AssetGlasses(
            **{
                "assetType": "outfit",
                "scenes": {
                    "properties": [
                        {
                            "name": "Validation",
                            "rootName": "Armature",
                            "bboxMin": [-0.46396, 0.00172, -0.12935],
                            "bboxMax": [0.46396, 1.5212, 0.19108],
                        }
                    ],
                    "hasDefaultScene": True,
                },
                "meshes": {
                    "properties": [
                        {
                            "name": "Wolf3D_Body",
                            "mode": ["TRIANGLES"],
                            "primitives": 1,
                            "glPrimitives": 1982,
                            "vertices": 1266,
                            "indices": ["u16"],
                            "attributes": [
                                "JOINTS_0:u8",
                                "NORMAL:f32",
                                "POSITION:f32",
                                "TEXCOORD_0:f32",
                                "WEIGHTS_0:f32",
                            ],
                            "instances": 1,
                            "size": 77724,
                        },
                        {
                            "name": "Wolf3D_Outfit_Bottom",
                            "mode": ["TRIANGLES"],
                            "primitives": 1,
                            "glPrimitives": 1790,
                            "vertices": 1295,
                            "indices": ["u16"],
                            "attributes": [
                                "JOINTS_0:u8",
                                "NORMAL:f32",
                                "POSITION:f32",
                                "TEXCOORD_0:f32",
                                "WEIGHTS_0:f32",
                            ],
                            "instances": 1,
                            "size": 78080,
                        },
                        {
                            "name": "Wolf3D_Outfit_Footwear",
                            "mode": ["TRIANGLES"],
                            "primitives": 1,
                            "glPrimitives": 2000,
                            "vertices": 1566,
                            "indices": ["u16"],
                            "attributes": [
                                "JOINTS_0:u8",
                                "NORMAL:f32",
                                "POSITION:f32",
                                "TEXCOORD_0:f32",
                                "WEIGHTS_0:f32",
                            ],
                            "instances": 1,
                            "size": 93432,
                        },
                        {
                            "name": "Wolf3D_Outfit_Top",
                            "mode": ["TRIANGLES"],
                            "primitives": 1,
                            "glPrimitives": 2998,
                            "vertices": 1794,
                            "indices": ["u16"],
                            "attributes": [
                                "JOINTS_0:u8",
                                "NORMAL:f32",
                                "POSITION:f32",
                                "TEXCOORD_0:f32",
                                "WEIGHTS_0:f32",
                            ],
                            "instances": 1,
                            "size": 111276,
                        },
                    ],
                    "hasMorphTargets": False,
                    "totalTriangleCount": 8770,
                },
                "materials": {
                    "properties": [
                        {
                            "name": "Wolf3D_Body",
                            "instances": 1,
                            "textures": ["normalTexture"],
                            "alphaMode": "OPAQUE",
                            "doubleSided": False,
                        },
                        {
                            "name": "Wolf3D_Outfit_Bottom",
                            "instances": 1,
                            "textures": ["baseColorTexture"],
                            "alphaMode": "OPAQUE",
                            "doubleSided": False,
                        },
                        {
                            "name": "Wolf3D_Outfit_Footwear",
                            "instances": 1,
                            "textures": ["baseColorTexture"],
                            "alphaMode": "OPAQUE",
                            "doubleSided": False,
                        },
                        {
                            "name": "Wolf3D_Outfit_Top",
                            "instances": 1,
                            "textures": ["baseColorTexture", "normalTexture"],
                            "alphaMode": "OPAQUE",
                            "doubleSided": False,
                        },
                    ],
                    "drawCallCount": 4,
                },
                "textures": {
                    "properties": [
                        {
                            "name": "Wolf3D-fullbody-f-N-1024",
                            "uri": "",
                            "slots": ["normalTexture"],
                            "instances": 1,
                            "mimeType": "image/jpeg",
                            "compression": "",
                            "resolution": "1024x1024",
                            "size": 450233,
                            "gpuSize": 5592404,
                        },
                        {
                            "name": "skirt_LOGO TIALSXBFF-C",
                            "uri": "",
                            "slots": ["baseColorTexture"],
                            "instances": 1,
                            "mimeType": "image/png",
                            "compression": "",
                            "resolution": "750x750",
                            "size": 61815,
                            "gpuSize": 2998156,
                        },
                        {
                            "name": "boots_LOGO TIALSXBFF-C",
                            "uri": "",
                            "slots": ["baseColorTexture"],
                            "instances": 1,
                            "mimeType": "image/jpeg",
                            "compression": "",
                            "resolution": "838x303",
                            "size": 24138,
                            "gpuSize": 1351776,
                        },
                        {
                            "name": "Shirt_N.png",
                            "uri": "",
                            "slots": ["normalTexture"],
                            "instances": 1,
                            "mimeType": "image/png",
                            "compression": "",
                            "resolution": "1024x1024",
                            "size": 1108322,
                            "gpuSize": 5592404,
                        },
                        {
                            "name": "Shirt_BC-C",
                            "uri": "",
                            "slots": ["baseColorTexture"],
                            "instances": 1,
                            "mimeType": "image/jpeg",
                            "compression": "",
                            "resolution": "1024x1024",
                            "size": 167644,
                            "gpuSize": 5592404,
                        },
                    ]
                },
                "animations": {"properties": []},
                "transforms": {
                    "Wolf3D_Body": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                    "Wolf3D_Outfit_Bottom": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                    "Wolf3D_Outfit_Footwear": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                    "Wolf3D_Outfit_Top": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                    "Armature": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                },
                "joints": {
                    "Hips": "Armature",
                    "Spine": "Hips",
                    "Spine1": "Spine",
                    "Spine2": "Spine1",
                    "Neck": "Spine2",
                    "Head": "Neck",
                    "HeadTop_End": "Head",
                    "LeftShoulder": "Spine2",
                    "LeftArm": "LeftShoulder",
                    "LeftForeArm": "LeftArm",
                    "LeftHand": "LeftForeArm",
                    "LeftHandThumb1": "LeftHand",
                    "LeftHandThumb2": "LeftHandThumb1",
                    "LeftHandThumb3": "LeftHandThumb2",
                    "LeftHandThumb4": "LeftHandThumb3",
                    "LeftHandIndex1": "LeftHand",
                    "LeftHandIndex2": "LeftHandIndex1",
                    "LeftHandIndex3": "LeftHandIndex2",
                    "LeftHandIndex4": "LeftHandIndex3",
                    "LeftHandMiddle1": "LeftHand",
                    "LeftHandMiddle2": "LeftHandMiddle1",
                    "LeftHandMiddle3": "LeftHandMiddle2",
                    "LeftHandMiddle4": "LeftHandMiddle3",
                    "LeftHandRing1": "LeftHand",
                    "LeftHandRing2": "LeftHandRing1",
                    "LeftHandRing3": "LeftHandRing2",
                    "LeftHandRing4": "LeftHandRing3",
                    "LeftHandPinky1": "LeftHand",
                    "LeftHandPinky2": "LeftHandPinky1",
                    "LeftHandPinky3": "LeftHandPinky2",
                    "LeftHandPinky4": "LeftHandPinky3",
                    "RightShoulder": "Spine2",
                    "RightArm": "RightShoulder",
                    "RightForeArm": "RightArm",
                    "RightHand": "RightForeArm",
                    "RightHandThumb1": "RightHand",
                    "RightHandThumb2": "RightHandThumb1",
                    "RightHandThumb3": "RightHandThumb2",
                    "RightHandThumb4": "RightHandThumb3",
                    "RightHandIndex1": "RightHand",
                    "RightHandIndex2": "RightHandIndex1",
                    "RightHandIndex3": "RightHandIndex2",
                    "RightHandIndex4": "RightHandIndex3",
                    "RightHandMiddle1": "RightHand",
                    "RightHandMiddle2": "RightHandMiddle1",
                    "RightHandMiddle3": "RightHandMiddle2",
                    "RightHandMiddle4": "RightHandMiddle3",
                    "RightHandRing1": "RightHand",
                    "RightHandRing2": "RightHandRing1",
                    "RightHandRing3": "RightHandRing2",
                    "RightHandRing4": "RightHandRing3",
                    "RightHandPinky1": "RightHand",
                    "RightHandPinky2": "RightHandPinky1",
                    "RightHandPinky3": "RightHandPinky2",
                    "RightHandPinky4": "RightHandPinky3",
                    "LeftUpLeg": "Hips",
                    "LeftLeg": "LeftUpLeg",
                    "LeftFoot": "LeftLeg",
                    "LeftToeBase": "LeftFoot",
                    "LeftToe_End": "LeftToeBase",
                    "RightUpLeg": "Hips",
                    "RightLeg": "RightUpLeg",
                    "RightFoot": "RightLeg",
                    "RightToeBase": "RightFoot",
                    "RightToe_End": "RightToeBase",
                    "neutral_bone": "Armature",
                },
                "gltfErrors": ["IMAGE_NPOT_DIMENSIONS"],
            }
        )

    except ValidationError as error:
        logging.debug("\nValidation Errors:\n %s" % error)
