#version 330 core

flat in int vertex_id;

uniform int frame_num;
uniform int joint_num;

in vec3 ourColor;
out vec4 FragColor;

int window_len = 100;

void main() {

    //int first_vertex_of_window = joint_num * (frame_num - window_len/2);
    //int final_vertex_of_window = joint_num * (frame_num + window_len/2);

    //discard if outside window
    //if((first_vertex_of_window <= vertex_id && vertex_id <= final_vertex_of_window) == false){
    //    discard;
    //}

    ////discard if not correct joint
    //if ((vertex_id % joint_num == 40) == false){
    //    discard;
    //}

    FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
