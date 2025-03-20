                experience = int(location_upgrade_xp * early_upgrade_xp_multiplier)
                keys = location_upgrade_keys
                
                game_state.player.gold -= cost
                game_state.player.experience += experience
                game_state.player.keys += keys
                
                cooldown_seconds = int(location.cooldown_seconds * self._config.cooldown_multiplier)
                next_upgrade_time = timestamp + cooldown_seconds
                
                logger.info(
                    f"Улучшение локации {location_id} до уровня {location.level}. "
                    f"Стоимость: {cost} золота. "
                    f"Получено: {experience} опыта, {keys} ключей. "
                    f"Баланс: {game_state.player.gold} золота."
                )
                
                if next_upgrade_time < self._config.session_duration_seconds:
                    logger.info(
                        f"Кулдаун: {cooldown_seconds} секунд. "
                        f"Следующее улучшение локации {location_id} будет доступно "
                        f"на {next_upgrade_time // 86400 + 1} день в "
                        f"{(next_upgrade_time % 86400) // 3600:02d}:"
                        f"{(next_upgrade_time % 3600) // 60:02d}:"
                        f"{(next_upgrade_time % 60):02d}"
                    )
                else:
                    logger.info(
                        f"Кулдаун: {cooldown_seconds} секунд. "
                        f"Следующее улучшение локации {location_id} будет доступно "
                        f"после завершения текущей сессии"
                    )
                
                location.next_upgrade_time = next_upgrade_time 