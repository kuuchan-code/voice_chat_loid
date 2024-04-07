#include <curl/curl.h>
#include <dpp/dpp.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
struct WavHeader {
  char riff[4];                 // "RIFF"
  unsigned int size;            // File size
  char wave[4];                 // "WAVE"
  char fmt[4];                  // "fmt "
  unsigned int fmtSize;         // Format chunk size
  unsigned short format;        // Format type
  unsigned short channels;      // Number of channels
  unsigned int sampleRate;      // Sample rate
  unsigned int byteRate;        // Byte rate
  unsigned short blockAlign;    // Block align
  unsigned short bitsPerSample; // Bits per sample
  char data[4];                 // "data"
  unsigned int dataSize;        // Data chunk size
};
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
std::vector<char> extractPCM(const std::string &wavData) {
  WavHeader header;

  // Ensure the data is large enough to contain a header
  if (wavData.size() < sizeof(WavHeader)) {
    std::cerr << "Error: WAV data is too small to contain header" << std::endl;
    return {};
  }

  // Copy the header from the WAV data
  std::memcpy(&header, wavData.data(), sizeof(header));

  // Check the WAV format
  if (std::strncmp(header.riff, "RIFF", 4) != 0 ||
      std::strncmp(header.wave, "WAVE", 4) != 0) {
    std::cerr << "Error: Invalid WAV format" << std::endl;
    return {};
  }

  // Extract PCM data
  std::vector<char> pcmData(wavData.begin() + sizeof(header), wavData.end());
  return pcmData;
}

int main() {
  /* Setup the bot */
  // 環境変数または設定ファイルからトークンを読み込む
  std::string token = std::getenv("DISCORD_BOT_TOKEN");
  dpp::cluster bot(token, dpp::i_default_intents | dpp::i_message_content);

  bot.on_log(dpp::utility::cout_logger());
  std::map<dpp::snowflake, dpp::snowflake> joined_channel_ids;
  /* The event is fired when someone issues your commands */
  bot.on_slashcommand([&bot,
                       &joined_channel_ids](const dpp::slashcommand_t &event) {
    /* Check which command they ran */
    if (event.command.get_command_name() == "join") {
      joined_channel_ids[event.command.guild_id] = event.command.channel_id;
      /* Get the guild */
      dpp::guild *g = dpp::find_guild(event.command.guild_id);

      /* Get the voice channel that the bot is currently in from this server
       * (will return nullptr if we're not in a voice channel!) */
      auto current_vc = event.from->get_voice(event.command.guild_id);

      bool join_vc = true;

      /* Are we in a voice channel? If so, let's see if we're in the right
       * channel. */
      if (current_vc) {
        /* Find the channel id that the user is currently in */
        auto users_vc =
            g->voice_members.find(event.command.get_issuing_user().id);

        if (users_vc != g->voice_members.end() &&
            current_vc->channel_id == users_vc->second.channel_id) {
          join_vc = false;

          /* We are on this voice channel, at this point we can send any audio
           instantly to vc:

           * current_vc->send_audio_raw(...)
           */
        } else {
          /* We are on a different voice channel. We should leave it, then join
           * the new one by falling through to the join_vc branch below.
           */
          event.from->disconnect_voice(event.command.guild_id);

          join_vc = true;
        }
      }

      /* If we need to join a vc at all, join it here if join_vc == true */
      if (join_vc) {
        /* Attempt to connect to a voice channel, returns false if we fail to
         * connect. */

        /* The user issuing the command is not on any voice channel, we can't do
         * anything */
        if (!g->connect_member_voice(event.command.get_issuing_user().id,
                                     /* self_mute= */ false,
                                     /* self_deaf= */ true)) {
          event.reply("You don't seem to be in a voice channel!");
          return;
        }

        /* We are now connecting to a vc. Wait for on_voice_ready
         * event, and then send the audio within that event:
         *
         * event.voice_client->send_audio_raw(...);
         *
         * NOTE: We can't instantly send audio, as we have to wait for
         * the connection to the voice server to be established!
         */

        /* Tell the user we joined their channel. */
        event.reply("Joined your channel!");
      } else {
        event.reply(
            "Don't need to join your channel as i'm already there with you!");
      }
    }
    if (event.command.get_command_name() == "playaudio") {
      // オーディオデータを再生するコマンドを処理
      CURL *curl;
      CURLcode res;
      std::string audio_query;
      std::string wavData;

      struct curl_slist *headers = NULL; // headersをメイン関数のスコープに移動

      curl_global_init(CURL_GLOBAL_DEFAULT);

      // 最初のリクエスト
      curl = curl_easy_init();
      if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL,
                         "http://localhost:50021/"
                         "audio_query?text=test123"
                         "&speaker=1");
        curl_easy_setopt(curl, CURLOPT_POST, 1L);

        headers = curl_slist_append(headers, "accept: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, "");
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &audio_query);
        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
          std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res)
                    << std::endl;
        } else {
          std::cout << "First Response:\n" << audio_query << std::endl;
        }
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
      } else {
        std::cerr << "Failed to initialize curl" << std::endl;
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
        // curl_easy_setopt(curl, CURLOPT_POSTFIELDS, audio_query.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &wavData);
        // 文字列をJSONオブジェクトに変換
        nlohmann::json jsonObj = nlohmann::json::parse(audio_query);

        // outputSamplingRateの値を変更
        jsonObj["outputSamplingRate"] = 96000;

        // JSONオブジェクトを文字列に戻す
        std::string modifiedJsonString = jsonObj.dump();

        // 結果を表示
        std::cout << modifiedJsonString << std::endl;

        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, modifiedJsonString.c_str());

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
          std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res)
                    << std::endl;
        } else {
          // バイナリデータのサイズを出力
          std::cout << "Second Response: Data size = " << wavData.size()
                    << " bytes" << std::endl;

          // 必要であれば、バイナリデータの一部を確認
          // 例：最初の10バイトを16進数で表示
          std::cout << "Data sample: ";
          std::cout << wavData.substr(0, 100);

          std::cout << std::endl;
        }
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
      } else {
        std::cerr << "Failed to initialize curl" << std::endl;
      }

      curl_global_cleanup();

      /* Get the voice channel the bot is in, in this current guild. */
      dpp::voiceconn *v = event.from->get_voice(event.command.guild_id);

      /* If the voice channel was invalid, or there is an issue with it, then
       * tell the user. */
      if (!v || !v->voiceclient || !v->voiceclient->is_ready()) {
        event.reply("There was an issue with getting the voice channel. Make "
                    "sure I'm in a voice channel!");
        return;
      }

      /* Stream the already decoded MP3 file. This passes the PCM data to the
       * library to be encoded to OPUS */

      // Reinterpret the char vector as uint16_t
      // WARNING: This assumes that the char vector's length is a multiple of 2
      // and may have alignment issues or endianess concerns.
      std::vector<char> pcmData = extractPCM(wavData);
      v->voiceclient->send_audio_raw((uint16_t *)pcmData.data(),
                                     pcmData.size());
      event.reply("Played the wav file.");
    }
  });
  bot.on_message_create(
      [&bot, &joined_channel_ids](const dpp::message_create_t &event) {
        // ギルドIDを取得
        dpp::snowflake guild_id = event.msg.guild_id;

        // マップから該当するテキストチャンネルIDを取得
        if (joined_channel_ids.find(guild_id) != joined_channel_ids.end() &&
            event.msg.channel_id == joined_channel_ids[guild_id]) {
          // チャンネルに新しいメッセージが投稿された場合の処理
          std::cout << "New message in joined channel: " << event.msg.content
                    << std::endl;
          // ここで必要な処理を実行
        }
      });

  bot.on_ready([&bot](const dpp::ready_t &event) {
    if (dpp::run_once<struct register_bot_commands>()) {
      /* Create a new command. */
      bot.guild_command_create(
          dpp::slashcommand("join", "Joins your voice channel.", bot.me.id),
          1190673139072516096);
      bot.guild_command_create(dpp::slashcommand("playaudio",
                                                 "Joins your voice channel.",
                                                 bot.me.id),
                               1190673139072516096);
    }
  });

  /* Start bot */
  bot.start(dpp::st_wait);

  return 0;
}
