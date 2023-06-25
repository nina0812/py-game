

def check_collision(self):
        # gledamo je li metak pogodio neprijatelja
        shoots = pg.sprite.groupcollide(self.enemy_sprites, self.bullet_sprites, True, True)
        if shoots:
            for shoot in shoots:
                self.score = self.update_score(self.score, shoot.points)
                self.make_coins()
                self.make_big_enemy()
                self.create_enemies(1)


                # moramo generirat nove neprijatelje nakon sto pogodimo metu jer se iz grupe sprite.group uklanjaju