// Copyright (c) Meta Platforms, Inc. and affiliates.

#version 330 core
layout(location = 0) in vec3 pos;
layout(location = 2) in vec2 texCoord;

out vec3 ourColor;
out vec2 TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

void main() {
    gl_Position = proj * view * model * vec4(pos, 1.0);
    TexCoord = texCoord;
}
