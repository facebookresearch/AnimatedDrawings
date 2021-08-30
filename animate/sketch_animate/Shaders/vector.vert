#version 330 core
//uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

uniform vec3 pc_centroid;

layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 color;

//in int gl_VertexID;
flat out int vertex_id;

out vec3 outColor;

void main(){
    //gl_Position = proj * view * model * vec4(pos, 1);
    gl_Position = proj * view * vec4(pos + pc_centroid, 1);

    vertex_id = gl_VertexID;

    outColor = color;
}
