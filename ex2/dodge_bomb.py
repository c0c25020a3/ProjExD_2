import os
import sys
import random
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内かどうかを判定する関数
    引数: 調べたいRectオブジェクト
    戻り値: 横方向と縦方向がそれぞれ画面内かどうか 
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の爆弾画像リストと加速度リストを返す関数
    戻り値: 爆弾画像のリストと加速度のリスト
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動方向に対応したこうかとん画像の辞書を返す関数
    戻り値: 移動量と画像のセット
    """
    kk_base = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    return {
        (0,   0): pg.transform.rotozoom(kk_base,   0, 1.0),
        (+5,  0): pg.transform.flip(kk_base, True, False),
        (+5, -5): pg.transform.rotozoom(kk_base,  45, 1.0),
        (0,  -5): pg.transform.rotozoom(kk_base, 270, 1.0),
        (-5, -5): pg.transform.rotozoom(kk_base, 315, 1.0),
        (-5,  0): pg.transform.rotozoom(kk_base,   0, 1.0),
        (-5, +5): pg.transform.rotozoom(kk_base,  45, 1.0),
        (0,  +5): pg.transform.rotozoom(kk_base,  90, 1.0),
        (+5, +5): pg.transform.rotozoom(kk_base, 135, 1.0),
    }


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を5秒間表示する関数
     引数: ゲーム画面のSurface
    """
    black_surf = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(black_surf, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    black_surf.set_alpha(200)

    font = pg.font.Font(None, 50)
    txt = font.render("Game Over", True, (255, 255, 255))
    black_surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 30))
    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    black_surf.blit(cry_img, (WIDTH//2 - 150, HEIGHT//2 - 50))
    black_surf.blit(cry_img, (WIDTH//2 + 100, HEIGHT//2 - 50))

    screen.blit(black_surf, (0, 0))
    pg.display.update()
    time.sleep(5)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    clock = pg.time.Clock()
    tmr = 0

    bb_img = pg.Surface((20, 20))
    bb_img.set_colorkey((0, 0, 0))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5
    bb_imgs, bb_accs = init_bb_imgs()

    kk_imgs = get_kk_imgs()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, [0, 0])
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for key, (dx, dy) in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += dx
                sum_mv[1] += dy

        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)
        yoko, tate = check_bound(kk_rct)
        if not yoko:
            kk_rct.move_ip(-sum_mv[0], 0)
        if not tate:
            kk_rct.move_ip(0, -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]

        old_center = bb_rct.center
        bb_rct = bb_img.get_rect()
        bb_rct.center = old_center

        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)

        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
