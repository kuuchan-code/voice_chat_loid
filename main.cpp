#include <dpp/dpp.h>
#include <zmq.hpp>
#include <string>
#include <iostream>

struct WavHeader
{
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
size_t Writeback(void *contents, size_t size, size_t nmemb, std::string *s)
{
  size_t newLength = size * nmemb;
  try
  {
    s->append((char *)contents, newLength);
    return newLength;
  }
  catch (std::bad_alloc &e)
  {
    return 0;
  }
}
std::vector<char> extractPCM(const std::string &wavData)
{
  WavHeader header;

  // Ensure the data is large enough to contain a header
  if (wavData.size() < sizeof(WavHeader))
  {
    std::cerr << "Error: WAV data is too small to contain header" << std::endl;
    return {};
  }

  // Copy the header from the WAV data
  std::memcpy(&header, wavData.data(), sizeof(header));

  // Check the WAV format
  if (std::strncmp(header.riff, "RIFF", 4) != 0 ||
      std::strncmp(header.wave, "WAVE", 4) != 0)
  {
    std::cerr << "Error: Invalid WAV format" << std::endl;
    return {};
  }

  // Extract PCM data
  std::vector<char> pcmData(wavData.begin() + sizeof(header), wavData.end());
  return pcmData;
}

int main()
{
  zmq::context_t context(1);
  zmq::socket_t socket(context, ZMQ_REQ);
  std::string connect_str = "tcp://localhost:5555";
  socket.connect(connect_str);
  /* Setup the bot */
  // 環境変数または設定ファイルからトークンを読み込む
  std::string token = std::getenv("DISCORD_BOT_TOKEN");
  dpp::cluster bot(token, dpp::i_default_intents | dpp::i_message_content);

  bot.on_log(dpp::utility::cout_logger());
  std::map<dpp::snowflake, dpp::snowflake> joined_channel_ids;
  /* The event is fired when someone issues your commands */
  bot.on_slashcommand([&bot,
                       &joined_channel_ids](const dpp::slashcommand_t &event)
                      {
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
    } });
  bot.on_message_create(
      [&bot, &joined_channel_ids, &socket](const dpp::message_create_t &event)
      {
        // ギルドIDを取得
        dpp::snowflake guild_id = event.msg.guild_id;

        // マップから該当するテキストチャンネルIDを取得
        if (joined_channel_ids.find(guild_id) != joined_channel_ids.end() &&
            event.msg.channel_id == joined_channel_ids[guild_id])
        {
          std::string raw_message = event.msg.content;
          zmq::message_t request(raw_message.data(), raw_message.size());
          socket.send(request, zmq::send_flags::none);
          zmq::message_t reply;
          auto result = socket.recv(reply, zmq::recv_flags::none); // ここでraw_messageの整形処理
          // チャンネルに新しいメッセージが投稿された場合の処理
          std::cout << "New message in joined channel: " << raw_message
                    << std::endl;
          // 受信結果を確認
          if (result)
          {
            std::string reply_str(static_cast<char *>(reply.data()), reply.size());
            std::cout << "Received: " << reply_str << std::endl;
          }
          else
          {
            std::cerr << "Failed to receive message" << std::endl;
          }
        }
      });

  bot.on_ready([&bot](const dpp::ready_t &event)
               {
    if (dpp::run_once<struct register_bot_commands>()) {
      /* Create a new command. */
      bot.guild_command_create(
          dpp::slashcommand("join", "Joins your voice channel.", bot.me.id),
          1190673139072516096);
    } });

  /* Start bot */
  bot.start(dpp::st_wait);

  return 0;
}
