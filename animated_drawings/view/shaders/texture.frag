// Copyright (c) Meta Platforms, Inc. and affiliates.

#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

uniform sampler2D texture0;

void main() {
    vec4 color = texture(texture0, TexCoord);

    if (color.a < 0.1){
        discard;
    }

    FragColor = color;
}
