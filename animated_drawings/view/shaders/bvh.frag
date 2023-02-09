// Copyright (c) Meta Platforms, Inc. and affiliates.

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
