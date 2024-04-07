#include <curl/curl.h>
#include <iostream>

size_t WriteCallback(void *contents, size_t size, size_t nmemb,
                     std::string *s) {
  size_t newLength = size * nmemb;
  try {
    s->append((char *)contents, newLength);
    return newLength;
  } catch (std::bad_alloc &e) {
    return 0;
  }
}

int main() {
  CURL *curl;
  CURLcode res;
  std::string readBuffer;
  struct curl_slist *headers = NULL; // headersをメイン関数のスコープに移動

  curl_global_init(CURL_GLOBAL_DEFAULT);

  // 最初のリクエスト
  curl = curl_easy_init();
  if (curl) {
    curl_easy_setopt(curl, CURLOPT_URL,
                     "http://localhost:50021/audio_query?text=a&speaker=1");
    curl_easy_setopt(curl, CURLOPT_POST, 1L);

    headers = curl_slist_append(headers, "accept: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, "");
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

    res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
      std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res)
                << std::endl;
    } else {
      std::cout << "First Response:\n" << readBuffer << std::endl;
    }
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
  }

  // 2回目のリクエスト
  headers = NULL; // headersをリセット
  curl = curl_easy_init();
  if (curl) {
    curl_easy_setopt(curl, CURLOPT_URL,
                     "http://localhost:50021/synthesis?speaker=1");
    curl_easy_setopt(curl, CURLOPT_POST, 1L);

    headers = curl_slist_append(headers, "accept: audio/wav");
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, readBuffer.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

    res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
      std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res)
                << std::endl;
    } else {
      // バイナリデータのサイズを出力
      std::cout << "Second Response: Data size = " << readBuffer.size()
                << " bytes" << std::endl;

      // 必要であれば、バイナリデータの一部を確認
      // 例：最初の10バイトを16進数で表示
      std::cout << "Data sample: ";
      for (size_t i = 0; i < 10 && i < readBuffer.size(); ++i) {
        std::cout << std::hex << static_cast<int>(readBuffer[i]) << " ";
      }
      std::cout << std::endl;
    }
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
  }

  curl_global_cleanup();

  return 0;
}