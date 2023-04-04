// Copyright (c) Meta Platforms, Inc. and affiliates.
// This source code is licensed under the MIT license found in the
// LICENSE file in the root directory of this source tree.

#version 330 core

flat in int vertex_id;

uniform int frame_num;
uniform int joint_num;

in vec3 ourColor;
out vec4 FragColor;


void main() {
    int first_vertex_of_frame = joint_num * frame_num;
    int final_vertex_of_frame = first_vertex_of_frame + joint_num;

    if (first_vertex_of_frame < vertex_id && vertex_id < final_vertex_of_frame){
        FragColor = vec4(ourColor, 1.0);
    }else{
        discard;
    }
}
