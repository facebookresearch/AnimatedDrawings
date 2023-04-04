// Copyright (c) Meta Platforms, Inc. and affiliates.
// This source code is licensed under the MIT license found in the
// LICENSE file in the root directory of this source tree.

#version 330 core
layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 color;

out vec3 ourColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

uniform bool color_black;

void main() {
    gl_Position = proj * view * model * vec4(pos, 1.0);
    if (color_black){
        ourColor = vec3(0.0, 0.0, 0.0);
    } else{
        ourColor = color;
    }
}
