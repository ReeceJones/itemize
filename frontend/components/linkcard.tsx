import { Card, Image, Text, Stack, UnstyledButton, AspectRatio, Grid, GridCol, Button, Space, Flex, ActionIcon, Popover, PopoverTarget, PopoverDropdown, Alert } from "@mantine/core"
import { useHover } from "@mantine/hooks"
import Link from "next/link"
import { Link as ILink, getItemize, ItemizeContext, deleteLinkFromItemize } from "@/util/api"
import { IconDotsVertical } from "@tabler/icons-react"
import { useState, useContext } from "react"


export default function LinkCard({link}: { link: ILink }) {
  const {hovered, ref} = useHover()
  const [linkDisabled, setLinkDisabled] = useState<boolean>(false)
  const [deleteLoading, setDeleteLoading] = useState<boolean>(false)
  const [deleteError, setDeleteError] = useState<string | undefined>(undefined)
  const {itemize, refreshItemize} = useContext(ItemizeContext)

  async function deleteLink() {
    setDeleteLoading(true)
    try {
      await deleteLinkFromItemize(itemize.owner, itemize.slug, link.id)
    } catch (error: any) {
      setDeleteError(error.message)
      setDeleteLoading(false)
      return
    }
    try {
      refreshItemize()
    } catch (error: any) {
      setDeleteError(error.message)
      setDeleteLoading(false)
      return
    }
    setDeleteLoading(false)
  }

  return (
    <UnstyledButton w="100%" component={Link} href={link.url} key={link.id} onClick={(e) => {
      if (hovered || linkDisabled) {
        e.preventDefault()
        e.stopPropagation()
      }
    }}>
      <Card shadow="sm" padding={0} radius="md" withBorder>
        <Grid>
          <GridCol span={2}>
            <AspectRatio ratio={1} miw={125}>
              <Image src={link.page_metadata.image_url} alt={link.page_metadata.description || ''}></Image>
            </AspectRatio>
          </GridCol>

          <GridCol span={10}>
            <Stack my={10}>
              {/* <Group justify="space-between" mr={10}> */}
              <Grid>
                <GridCol span={11}>
                    <Text fw={500}>{link.page_metadata.title}</Text>
                </GridCol>
                <GridCol span={1}>
                  <Flex justify="flex-end" mx={10}>
                    <div ref={ref}>
                      <Popover width={200} onOpen={() => setLinkDisabled(true)} onClose={() => setLinkDisabled(false)}>
                        <PopoverTarget>
                          <ActionIcon variant="subtle" color="dark"><IconDotsVertical size={18}/></ActionIcon>
                        </PopoverTarget>
                        <PopoverDropdown>
                          <Button fullWidth disabled>Edit</Button>
                          <Space h={10}/>
                          <Button color="red" loading={deleteLoading} onClick={deleteLink} fullWidth>Delete</Button>
                          {
                            deleteError && (
                              <>
                                <Space h={10}/>
                                <Alert color="red" title="Error">{deleteError}</Alert>
                              </>
                            )
                          }
                        </PopoverDropdown>
                      </Popover>
                    </div>
                  </Flex>
                </GridCol>
              </Grid>
              {/* </Group> */}
              <Text size="sm" c="dimmed" lineClamp={3}>{link.page_metadata.description || ''}</Text>
            </Stack>
          </GridCol>
        </Grid>
      </Card>
    </UnstyledButton>
  )
}