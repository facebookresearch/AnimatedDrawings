// Copyright (c) Meta Platforms, Inc. and affiliates.

#version 330 core
uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 color;

flat out int vertex_id;

out vec3 ourColor;

void main(){
   gl_Position = proj * view * model * vec4(pos, 1);

   vertex_id = gl_VertexID;

   ourColor = color;
}
