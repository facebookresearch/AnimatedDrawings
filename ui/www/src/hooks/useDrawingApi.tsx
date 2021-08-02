import axios, { AxiosRequestConfig } from "axios";
import { useEffect, useState } from "react";
// import fs from "fs";

export function useDrawingApi(onError: (error: Error) => void) {
  const [isLoading, setIsLoading] = useState(false);

  const apiHost = process.env.REACT_APP_API_HOST;
  console.log(process.env);

  enum ApiPath {
    UploadImage = "upload_image",
    GetAnimation = "get_animation",
  }

  const DEFAULT_CONFIG = {
    timeout: 60000,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  };

  async function invokePost(
    path: string,
    data: any,
    onResult: (result: any) => void,
    config: AxiosRequestConfig = DEFAULT_CONFIG
  ) {
    try {
      setIsLoading(true);

      const result = await axios.post(`${apiHost}/${path}`, data, config);
      onResult(result.data);
    } catch (error) {
      console.log(error);
      onError(error);
    } finally {
      setIsLoading(false);
    }
  }

  const uploadImage = async function (
    file: File,
    onResult: (result: any) => void
  ) {
    const form = new FormData();
    if (file !== null) {
      form.append("file", file);
    }
    await invokePost(ApiPath.UploadImage, form, onResult);
  };

  const getAnimation = async function (
    uuid: string,
    onResult: (result: any) => void
  ) {
    // try {

    const form = new FormData();
    form.set("animation", "wave");
    if (uuid) {
      form.set("uuid", uuid);
    }
    await invokePost(ApiPath.GetAnimation, form, onResult, {
      ...DEFAULT_CONFIG,
      responseType: "arraybuffer",
    });
  };

  return {
    isLoading,
    uploadImage,
    getAnimation,
  };
}
