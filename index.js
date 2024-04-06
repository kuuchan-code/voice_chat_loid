const { joinVoiceChannel, getVoiceConnection } = require('@discordjs/voice')

require('dotenv').config()

const joinCommand = require('./commands/join')

const { Client, Events, GatewayIntentBits } = require('discord.js')

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildVoiceStates] })

client.once(Events.ClientReady, readyClient => {
  console.log(`Ready! Logged in as ${readyClient.user.tag}`)
})

client.login(process.env.DISCORD_TOKEN)

client.on('interactionCreate', async interaction => {
  if (interaction.isCommand()) {
    joinCommand.execute(interaction, client)
  } else if (interaction.isButton()) {
    if (interaction.customId === 'join_confirm') {
      const voiceChannel = interaction.member.voice.channel

      if (voiceChannel) {
        // Check if the bot is already connected to a voice channel in this guild
        const existingConnection = getVoiceConnection(voiceChannel.guild.id)
        if (existingConnection) {
          // If so, destroy the existing connection to disconnect
          existingConnection.destroy()
        }

        // Connect to the new voice channel
        joinVoiceChannel({
          channelId: voiceChannel.id,
          guildId: voiceChannel.guild.id,
          adapterCreator: voiceChannel.guild.voiceAdapterCreator
        })

        await interaction.reply({ content: 'ボイスチャンネルに接続しました。' })
      } else {
        await interaction.reply({ content: 'ボイスチャンネルにいる必要があります。', ephemeral: true })
      }
    } else if (interaction.customId === 'join_decline') {
      await interaction.reply({ content: '操作がキャンセルされました。', ephemeral: true })
    }
  }
})
