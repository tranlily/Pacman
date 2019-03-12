import pygame


class ImageManager:
    def __init__(self, img, sheet=False, pos_offsets=None,
                 resize=None, keys=None,
                 convert=True, transparency=True,
                 animation_delay=None, reversible=False,
                 repeat=True):
        if not sheet:
            self.images = [pygame.image.load('images/' + img)]
        else:
            self.sheet = pygame.image.load('images/' + img)
            self.pos_offsets = pos_offsets
            self.images = self.extract_images()
        if resize:
            self.images = [pygame.transform.scale(img, resize) for img in self.images]
        self.rect = self.images[0].get_rect()
        if convert:
            self.images = [img.convert() for img in self.images]
        if transparency:
            for i in self.images:
                i.set_colorkey((0, 0, 0, 0))
        if keys:
            if not len(keys) == len(self.images):
                raise ValueError('Must provide same number of keys as images')
            images_dict = dict()
            for k, i in zip(keys, range(len(self.images))):
                images_dict[k] = self.images[i]
            self.images = images_dict
        else:
            self.image_index = 0
        self.change_animation = animation_delay
        self.get_ticks = pygame.time.get_ticks()
        self.flip_image = reversible
        self.repeat = repeat

    def get_image(self, key=None):
        if isinstance(self.images, list):
            return self.images[self.image_index], self.rect
        else:
            if not key:
                raise KeyError('No image key provided')
            return self.images[key], self.rect

    def extract_images(self):
        if not self.sheet:
            raise ValueError('Image manager has no sprite sheet to extract images from')
        result = []
        for rect in self.pos_offsets:
            select = pygame.Rect(rect)
            sub_image = pygame.Surface(select.size).convert(pygame.display.get_surface())
            sub_image.blit(self.sheet, (0, 0), select)
            result.append(sub_image)
        return result

    def next_image(self):
        if not isinstance(self.images, list):
            raise ValueError('next_image not callable when using keys')
        if not self.repeat and self.image_index + 1 >= len(self.images):
            return self.images[self.image_index]
        if self.flip_image and self.image_index + 1 >= len(self.images):
            self.images.reverse()
        if not self.change_animation:
            self.image_index = (self.image_index + 1) % len(self.images)
        else:
            if abs(self.get_ticks - pygame.time.get_ticks()) > self.change_animation:
                self.image_index = (self.image_index + 1) % len(self.images)
                self.get_ticks = pygame.time.get_ticks()

        return self.images[self.image_index]

    def flip(self, x_bool=True, y_bool=False):
        if isinstance(self.images, dict):
            self.images = {v: pygame.transform.flip(v, x_bool, y_bool) for k, v in self.images.items()}
        else:
            self.images = [pygame.transform.flip(x, x_bool, y_bool) for x in self.images]

    def all_images(self):
        return self.images
