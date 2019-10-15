use serde::{Deserialize, Serialize};
/**
package pw.cub3d.uk.pushMessaging

enum class PushMessagePriority {
    MINIMUM,
    LOW,
    DEFAULT,
    MEDIUM,
    HIGH,
    MAXIMUM
}

data class PushMessagePayloadEntry(
    val key: String,
    val value: String
)

data class PushMessagePayload(
    val title: String,
    val content: String,
    val icon: String?,
    val clickIntent: String?
)

data class PushMessage(
    val targetAppID: String,
    val priority: PushMessagePriority?,
    val requiresAcknowledge: Boolean?,
    val message: PushMessagePayload?,
    val dataPayload: Array<PushMessagePayloadEntry>?
)
**/

#[derive(Serialize, Deserialize, Debug)]
pub struct PushMessagePayloadEntry {
    pub key: String,
    pub value: String
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Notification {
    pub targetAppID: String,
//    pub priority: NotificationPrioritory,
//    pub requiresAcknoqledge: bool,
//    pub message: PushMessagePayload,
    pub dataPayload: Option<Vec<PushMessagePayloadEntry>>
}
